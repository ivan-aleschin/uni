# ТАЯК, ЛР1. Синтаксический анализатор и калькулятор арифметических выражений.
# Четыре этапа — четыре функции, классов с поведением нет.
#
# Путь строки через программу:
#   строка -> tokenize() -> лексемы -> check() -> проверенные лексемы
#          -> to_rpn() (алгоритм Дейкстры) -> ОПЗ -> evaluate() -> число
#
# Ошибка на любом этапе бросается как ExprError с позицией в строке,
# main ловит её и показывает, где именно ошибка.

import math
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

# ============================================================================
# Встроенная функция. ВСЁ, что про неё знает программа, — здесь.
# Чтобы заменить log на pow (или любую другую функцию двух аргументов),
# достаточно поменять имя, формулу и проверку области определения ниже.
# ============================================================================

ARITY = 2  # число аргументов встроенной функции (по заданию — две)


@dataclass(frozen=True)
class BuiltinFunction:
    name: str                                         # как функция пишется в выражении
    apply: Callable[[float, float], float]            # формула
    domain_error: Callable[[float, float], str | None]  # None, если аргументы допустимы


# log(a, b) — логарифм числа b по основанию a.
BUILTIN = BuiltinFunction(
    "log",
    lambda a, b: math.log(b) / math.log(a),
    lambda a, b: (
        "основание логарифма должно быть > 0 и не равно 1" if a <= 0 or a == 1 else
        "под логарифмом должно быть положительное число" if b <= 0 else
        None
    ),
)

# Вариант для замены по требованию преподавателя — закомментировать log выше
# и раскомментировать это:
#
# BUILTIN = BuiltinFunction(
#     "pow",
#     lambda a, b: math.pow(a, b),
#     lambda a, b: (
#         "ноль нельзя возводить в отрицательную степень" if a == 0 and b < 0 else
#         "отрицательное число нельзя возводить в дробную степень" if a < 0 and b != math.floor(b) else
#         None
#     ),
# )

# ============================================================================
# Лексемы и ошибки
# ============================================================================


class Kind(Enum):
    NUMBER = auto()   # действительное число: 12, 66.6, .54, 221.
    PLUS = auto()     # бинарные + - * /
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    NEG = auto()      # унарный минус (лексер его не различает, его выставляет check)
    LPAREN = auto()   # ( ) ,
    RPAREN = auto()
    COMMA = auto()
    FUNC = auto()     # имя встроенной функции
    END = auto()      # конец строки — чтобы ошибку "выражение оборвалось" было куда привязать


@dataclass
class Token:
    kind: Kind
    text: str          # как лексема записана во входной строке
    pos: int           # номер символа в строке (с нуля), нужен для сообщения об ошибке
    value: float = 0.0  # значение, только для NUMBER


class ExprError(Exception):
    def __init__(self, pos: int, message: str):
        super().__init__(message)
        self.pos = pos
        self.message = message


# ============================================================================
# 1. Лексический анализ: строка -> список лексем
# ============================================================================

# Только ASCII: у стандартных str.isdigit() и
# str.isalpha() цифрами и буквами считаются и '٣', и русские буквы.
DIGITS = "0123456789"
NAME_START = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
NAME_CHARS = NAME_START + DIGITS

SINGLE = {  # односимвольные лексемы
    "+": Kind.PLUS, "-": Kind.MINUS, "*": Kind.STAR, "/": Kind.SLASH,
    "(": Kind.LPAREN, ")": Kind.RPAREN, ",": Kind.COMMA,
}


def tokenize(s: str) -> list[Token]:
    tokens = []
    i = 0
    while i < len(s):  # ЦИКЛ по символам строки
        c = s[i]
        start = i

        if c in " \t":  # пробелы просто пропускаем
            i += 1
            continue

        # Число: подряд идущие цифры и точки. Забираем всё целиком и потом
        # проверяем, чтобы "1.2.3" было одной ошибкой, а не двумя числами.
        if c in DIGITS or c == ".":
            while i < len(s) and (s[i] in DIGITS or s[i] == "."):
                i += 1
            text = s[start:i]
            if text.count(".") > 1 or text == ".":
                raise ExprError(start, f"некорректное число '{text}'")
            # float() не ругается на выход за пределы double, а молча даёт inf или 0.0.
            # Ловим оба случая сами: это то же, что result_out_of_range у from_chars.
            value = float(text)
            huge = math.isinf(value)
            if huge or (value == 0 and text.strip("0.")):  # ноль, хотя в записи есть ненулевая цифра
                raise ExprError(start, f"слишком {'большое' if huge else 'близкое к нулю'} число '{text}'")
            tokens.append(Token(Kind.NUMBER, text, start, value))
            continue

        # Имя: буквы, цифры, '_'. Допустимо только имя встроенной функции.
        if c in NAME_START:
            while i < len(s) and s[i] in NAME_CHARS:
                i += 1
            name = s[start:i]
            if name != BUILTIN.name:
                raise ExprError(start, f"неизвестное имя '{name}' (есть только функция {BUILTIN.name})")
            tokens.append(Token(Kind.FUNC, name, start))
            continue

        if c not in SINGLE:  # РАЗВИЛКА по символу
            raise ExprError(start, f"недопустимый символ '{c}'")
        tokens.append(Token(SINGLE[c], c, start))
        i += 1
    tokens.append(Token(Kind.END, "конец строки", len(s)))
    return tokens


# ============================================================================
# 2. Синтаксическая проверка
#
# Идём по лексемам и помним одно: что сейчас ожидается — ОПЕРАНД (число,
# '(', функция, унарный минус) или ОПЕРАЦИЯ (+ - * /, ')', ',', конец).
# Плюс стек открытых скобок: для скобки функции считаем аргументы.
# Попутно минус в позиции операнда помечается как унарный (Kind.NEG).
# ============================================================================

OPERATORS = {Kind.PLUS, Kind.MINUS, Kind.STAR, Kind.SLASH, Kind.NEG}


# Текст ошибки "здесь должен был быть операнд, а стоит cur".
# Разбираем частные случаи, чтобы сообщение было понятным.
def missing_operand_message(t: list[Token], i: int) -> str:
    cur = t[i]
    if i == 0:
        return "пустое выражение" if cur.kind == Kind.END else f"выражение не может начинаться с '{cur.text}'"
    prev = t[i - 1]
    if cur.kind == Kind.END:
        return f"выражение оборвалось: после '{prev.text}' ожидается операнд"
    if prev.kind in OPERATORS:
        return f"два знака операции подряд: '{prev.text}' и '{cur.text}'"
    if prev.kind == Kind.LPAREN and cur.kind == Kind.RPAREN:
        if i >= 2 and t[i - 2].kind == Kind.FUNC:
            return f"у функции {t[i - 2].text} нет аргументов"
        return "пустые скобки '()'"
    if cur.kind in (Kind.COMMA, Kind.RPAREN):
        return "пропущен аргумент функции"  # "log(,2)", "log(2,)"
    return f"после '{prev.text}' ожидается операнд, а стоит '{cur.text}'"


@dataclass
class Paren:
    pos: int       # где открыта — для ошибки "не закрыта"
    is_func: bool  # скобка функции?
    args: int      # сколько аргументов уже начато


def check(t: list[Token]) -> None:
    parens: list[Paren] = []
    expect_operand = True

    i = 0
    while i < len(t):  # ЦИКЛ по лексемам (не for: на функции перескакиваем через её '(')
        cur = t[i]

        if expect_operand:  # РАЗВИЛКА: ждём операнд
            match cur.kind:
                case Kind.NUMBER:
                    expect_operand = False
                case Kind.MINUS:  # минус там, где ждём операнд, — унарный
                    cur.kind = Kind.NEG
                case Kind.LPAREN:
                    parens.append(Paren(cur.pos, False, 0))
                case Kind.FUNC:  # после имени функции обязательно '('
                    if t[i + 1].kind != Kind.LPAREN:
                        raise ExprError(t[i + 1].pos, f"после имени функции {cur.text} ожидается '('")
                    i += 1
                    parens.append(Paren(t[i].pos, True, 1))
                case _:
                    raise ExprError(cur.pos, missing_operand_message(t, i))
        else:  # РАЗВИЛКА: ждём операцию
            match cur.kind:
                case Kind.PLUS | Kind.MINUS | Kind.STAR | Kind.SLASH:
                    expect_operand = True
                case Kind.RPAREN:
                    if not parens:
                        raise ExprError(cur.pos, "лишняя ')': для неё нет парной '('")
                    if parens[-1].is_func and parens[-1].args != ARITY:
                        raise ExprError(cur.pos, f"функция {BUILTIN.name} принимает {ARITY} аргумента, "
                                                 f"а передано {parens[-1].args}")
                    parens.pop()
                case Kind.COMMA:
                    if not parens or not parens[-1].is_func:
                        raise ExprError(cur.pos, "запятая вне скобок функции")
                    parens[-1].args += 1
                    expect_operand = True
                case Kind.END:
                    if parens:
                        raise ExprError(parens[-1].pos, "не закрыта '(': не хватает ')'")
                case _:  # число, '(' или функция сразу после операнда
                    raise ExprError(cur.pos, f"пропущен знак операции между '{t[i - 1].text}' и '{cur.text}'")
        i += 1


# ============================================================================
# 3. Перевод в обратную польскую запись (алгоритм Дейкстры)
#
# Стековые приоритеты — табл. 1 методички, дополненная унарным минусом
# и функцией:  ( ) — 1,  + - — 2,  * / — 3,  унарный минус — 4,  функция — 5.
# ============================================================================

PRIORITY = {
    Kind.LPAREN: 1, Kind.RPAREN: 1,
    Kind.PLUS: 2, Kind.MINUS: 2,
    Kind.STAR: 3, Kind.SLASH: 3,
    Kind.NEG: 4,
    Kind.FUNC: 5,
}


def join_texts(v: list[Token], neg: str) -> str:
    return " ".join(neg if t.kind == Kind.NEG else t.text for t in v)


# Строку проверили в check(), поэтому здесь ошибок быть не может.
# trace = True печатает таблицу как на рис. 2 методички.
def to_rpn(t: list[Token], trace: bool) -> list[Token]:
    out: list[Token] = []
    stack: list[Token] = []

    if trace:
        print(f"  {'символ':<14}{'стек (верх справа)':<22}выход")

    for cur in t:  # ЦИКЛ по лексемам
        match cur.kind:  # РАЗВИЛКА по типу лексемы
            case Kind.NUMBER:  # операнд — сразу в выходную строку
                out.append(cur)
            case Kind.LPAREN | Kind.FUNC | Kind.NEG:
                # правило c): '(' — в стек; функция и унарный минус префиксные: перед ними
                # в стеке нет ничего, что пора вычислять, — тоже просто в стек
                stack.append(cur)
            case Kind.COMMA:  # запятая закрывает аргумент: выталкиваем до '(' функции
                while stack[-1].kind != Kind.LPAREN:
                    out.append(stack.pop())
            case Kind.RPAREN:  # правило d): выталкиваем до '(', скобки уничтожают друг друга
                while stack[-1].kind != Kind.LPAREN:
                    out.append(stack.pop())
                stack.pop()
                if stack and stack[-1].kind == Kind.FUNC:
                    out.append(stack.pop())
            case Kind.END:  # конец строки: всё, что осталось, — в выход
                while stack:
                    out.append(stack.pop())
            case _:  # бинарная операция, правило b): выталкиваем всё с приоритетом >=
                while stack and PRIORITY[stack[-1].kind] >= PRIORITY[cur.kind]:
                    out.append(stack.pop())
                stack.append(cur)
        if trace:
            symbol = "-(унарный)" if cur.kind == Kind.NEG else cur.text
            print(f"  {symbol:<14}{join_texts(stack, '~'):<22}{join_texts(out, '~')}")
    return out


# ============================================================================
# 4. Вычисление ОПЗ на стеке
# ============================================================================

def format_number(x: float) -> str:
    if x == 0:
        x = 0.0  # чтобы не печатать "-0"
    return f"{x:.12g}"  # до 12 значащих цифр, без хвостовых нулей


def evaluate(rpn: list[Token]) -> float:
    stack: list[float] = []

    for t in rpn:  # ЦИКЛ по ОПЗ слева направо
        match t.kind:  # РАЗВИЛКА
            case Kind.NUMBER:
                stack.append(t.value)
            case Kind.NEG:
                stack[-1] = -stack[-1]
            case Kind.FUNC:
                b, a = stack.pop(), stack.pop()  # на вершине — последний аргумент
                if err := BUILTIN.domain_error(a, b):
                    raise ExprError(t.pos, f"{BUILTIN.name}({format_number(a)}, {format_number(b)}): {err}")
                try:
                    stack.append(BUILTIN.apply(a, b))
                except OverflowError:  # math.pow при переполнении бросает исключение, а не даёт inf
                    stack.append(math.inf)
            case _:  # бинарная операция
                b, a = stack.pop(), stack.pop()
                match t.kind:
                    case Kind.PLUS:
                        stack.append(a + b)
                    case Kind.MINUS:
                        stack.append(a - b)
                    case Kind.STAR:
                        stack.append(a * b)
                    case _:
                        if b == 0:
                            raise ExprError(t.pos, "деление на ноль")
                        stack.append(a / b)
        if not math.isfinite(stack[-1]):
            raise ExprError(t.pos, "переполнение: результат не помещается в double")
    return stack[-1]


# ============================================================================
# Ввод-вывод
# ============================================================================

# Отступ для стрелки ^ под символом номер pos: по пробелу на каждый символ левее,
# табуляция копируется как есть, иначе стрелка съедет. В Python строка уже
# состоит из символов, а не байт, поэтому UTF-8 отдельно учитывать не нужно.
def caret_pad(s: str, pos: int) -> str:
    return "".join("\t" if ch == "\t" else " " for ch in s[:pos])


def process(line: str, trace: bool) -> None:
    stage = "Синтаксическая ошибка"
    try:
        tokens = tokenize(line)
        check(tokens)
        print("Выражение корректно.")
        rpn = to_rpn(tokens, trace)
        print("ОПЗ:", join_texts(rpn, "~"))
        stage = "Ошибка вычисления"
        result = evaluate(rpn)
        print("Результат:", format_number(result))
    except ExprError as e:
        pad = caret_pad(line, e.pos)
        print(f"{stage} в позиции {len(pad) + 1}: {e.message}")
        print("  " + line)
        print("  " + pad + "^")


def main() -> None:
    trace = len(sys.argv) > 1 and sys.argv[1] == "--trace"
    interactive = sys.stdin.isatty()  # отличаем ввод с клавиатуры от printf | python3 main.py

    # Читаем и пишем UTF-8 независимо от локали. newline="\n": строку завершает только
    # '\n'; иначе Python сам превратил бы '\r' в конец строки.
    sys.stdin.reconfigure(encoding="utf-8", errors="surrogateescape", newline="\n")
    sys.stdout.reconfigure(encoding="utf-8", errors="surrogateescape", newline="\n")

    if interactive:
        print(f"Калькулятор: + - * /, скобки, числа вида 12, 66.6, .54, 221., "
              f"функция {BUILTIN.name}(a, b).\nПустая строка или Ctrl+D — выход.")

    while True:  # ЦИКЛ: строка за строкой до EOF (с клавиатуры — и до пустой строки)
        if interactive:
            print("> ", end="", flush=True)
        line = sys.stdin.readline()
        if not line:
            break
        line = line.removesuffix("\n").removesuffix("\r")  # '\r' — файлы из Windows
        if not line and interactive:
            break  # из файла пустая строка — это "пустое выражение"
        if not interactive:
            print("> " + line)  # эхо, чтобы в выводе было видно выражение
        process(line, trace)
        print()


if __name__ == "__main__":
    main()
