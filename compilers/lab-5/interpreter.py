"""Интерпретатор CBAS: выполняет программу прямо по списку лексем во внутреннем формате.

Каждая функция process_* получает флаг ex («выполнять»). При ex=False она только
разбирает свою конструкцию и сдвигает указатель — так проверяется синтаксис всей программы
до запуска и так же пропускаются невыполняемые ветки if и тело цикла при выходе из него.
"""

import re
import sys
from typing import TextIO

from lexer import INT_MAX, INT_MIN, CbasError, Tok, Token, kind

RELOPS = {Tok.LT, Tok.GT, Tok.EQ, Tok.NE}
INT_RE = re.compile(r"[+-]?[0-9]+")


def describe(tok: Token) -> str:
    """Как назвать лексему в сообщении об ошибке."""
    if tok.code == Tok.END:
        return "конец программы"
    if tok.code == Tok.STRING:
        return f"строка {tok.text}"
    return f"{kind(tok.code)} '{tok.text}'"


class Interpreter:
    def __init__(self, tokens: list[Token], stdin: TextIO = sys.stdin,
                 stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> None:
        self.tokens = tokens
        self.pos = 0  # указатель на текущее место программы (номер лексемы)
        self.variables: dict[str, int] = {}  # таблица переменных «имя — значение»
        self.stdin, self.stdout, self.stderr = stdin, stdout, stderr
        self.input_words: list[str] = []  # уже введённые, но ещё не прочитанные scan числа

    # ---------- работа с потоком лексем ----------

    def get_token(self) -> Token:
        tok = self.tokens[min(self.pos, len(self.tokens) - 1)]  # за концом всегда END
        self.pos += 1
        return tok

    def putback(self) -> None:
        """Вернуть последнюю лексему во входной поток."""
        self.pos -= 1

    def expect(self, code: Tok, what: str) -> Token:
        tok = self.get_token()
        if tok.code != code:
            raise CbasError(tok.line, f"ожидалось {what}, а встретилось {describe(tok)}")
        return tok

    # ---------- операторы ----------

    def run(self) -> None:
        # проход 1: только проверка синтаксиса, ничего не выполняется и не печатается
        self.pos = 0
        self.statements(False, None)
        # проход 2: выполнение
        self.pos = 0
        self.statements(True, None)

    def statements(self, ex: bool, opener: Token | None) -> None:
        """Главный цикл: читает лексему и вызывает нужную функцию. Работает до '}' своего блока
        (opener — открывшая блок '{') или до конца программы (opener = None)."""
        while True:
            tok = self.get_token()
            match tok.code:
                case Tok.PRINT:
                    self.process_print(ex)
                case Tok.SCAN:
                    self.process_scan(ex)
                case Tok.IDENT:
                    self.process_assign(tok, ex)
                case Tok.FOR:
                    self.process_for(ex)
                case Tok.IF:
                    self.process_if(ex)
                case Tok.RBRACE:
                    if opener is None:
                        raise CbasError(tok.line, "лишняя '}' без парной '{'")
                    return
                case Tok.END:
                    if opener is not None:
                        raise CbasError(opener.line, "'{' не закрыта: не хватает '}'")
                    return
                case Tok.ELSE:
                    raise CbasError(tok.line, "else без if (else пишется сразу после '}' блока if)")
                case _:
                    raise CbasError(tok.line, "ожидался оператор (print, scan, for, if или "
                                              f"присваивание), а встретилось {describe(tok)}")

    def block(self, ex: bool) -> None:
        """'{' <statement> '}'"""
        opener = self.expect(Tok.LBRACE, "'{'")
        self.statements(ex, opener)

    def process_print(self, ex: bool) -> None:
        """print <элемент> {',' <элемент>} ';' — элемент: строка или выражение."""
        parts: list[str] = []
        while True:
            tok = self.get_token()
            if tok.code == Tok.STRING:
                parts.append(str(tok.value))
            else:
                self.putback()  # это начало выражения — вернуть лексему и вычислить
                parts.append(str(self.expression(ex)))
            tok = self.get_token()
            if tok.code == Tok.SEMI:
                break
            if tok.code != Tok.COMMA:
                raise CbasError(tok.line, f"в print ожидалась ',' или ';', а встретилось {describe(tok)}")
        if ex:
            print("".join(parts), file=self.stdout)

    def process_scan(self, ex: bool) -> None:
        """scan <identifier> ';'"""
        var = self.expect(Tok.IDENT, "имя переменной после scan")
        self.expect(Tok.SEMI, "';' после scan")
        if ex:
            self.variables[str(var.value)] = self.read_int(var.line)

    def process_assign(self, var: Token, ex: bool) -> None:
        """<identifier> '=' <expression> [';']"""
        self.expect(Tok.ASSIGN, f"'=' после имени {var.text}")
        value = self.expression(ex)
        if ex:
            self.variables[str(var.value)] = value
        if self.get_token().code != Tok.SEMI:  # ';' после присваивания необязательна
            self.putback()

    def process_for(self, ex: bool) -> None:
        """for <identifier> '=' <expression> to <expression> '{' <statement> '}'"""
        var = self.expect(Tok.IDENT, "имя переменной цикла после for")
        self.expect(Tok.ASSIGN, "'=' после переменной цикла")
        start = self.expression(ex)
        self.expect(Tok.TO, "ключевое слово 'to'")
        target = self.expression(ex)  # граница вычисляется один раз, при входе в цикл
        body = self.pos  # место начала тела — сюда возвращаемся на каждой итерации
        name = str(var.value)
        if ex:
            self.variables[name] = start
            while self.variables[name] < target:  # выход, когда переменная >= границы
                self.pos = body
                self.block(True)
                self.variables[name] = self.check_int(self.variables[name] + 1, var.line)
        # тело ещё раз «вхолостую» — чтобы встать за его '}' (и проверить синтаксис на проходе 1)
        self.pos = body
        self.block(False)

    def process_if(self, ex: bool) -> None:
        """if <bool_expression> '{' <statement> '}' [else '{' <statement> '}']"""
        cond = self.bool_expression(ex)
        self.block(ex and cond)
        if self.get_token().code == Tok.ELSE:
            self.block(ex and not cond)
        else:
            self.putback()

    # ---------- выражения: рекурсивный спуск ----------

    def bool_expression(self, ex: bool) -> bool:
        """<expression> <relop> <expression>"""
        left = self.expression(ex)
        op = self.get_token()
        if op.code not in RELOPS:
            raise CbasError(op.line, "в условии ожидалась операция сравнения (<, >, ==, !=), "
                                     f"а встретилось {describe(op)}")
        right = self.expression(ex)
        match op.code:
            case Tok.LT:
                return left < right
            case Tok.GT:
                return left > right
            case Tok.EQ:
                return left == right
            case _:
                return left != right

    def expression(self, ex: bool) -> int:
        """Выражение => Терм {('+' | '-') Терм}"""
        value = self.term(ex)
        while True:
            op = self.get_token()
            if op.code == Tok.PLUS:
                value = self.check_int(value + self.term(ex), op.line)
            elif op.code == Tok.MINUS:
                value = self.check_int(value - self.term(ex), op.line)
            else:
                self.putback()
                return value

    def term(self, ex: bool) -> int:
        """Терм => Фактор {('*' | '/') Фактор}"""
        value = self.factor(ex)
        while True:
            op = self.get_token()
            if op.code == Tok.MUL:
                value = self.check_int(value * self.factor(ex), op.line)
            elif op.code == Tok.DIV:
                divisor = self.factor(ex)
                if ex and divisor == 0:
                    raise CbasError(op.line, "деление на ноль", runtime=True)
                if ex:  # деление как в C: дробная часть отбрасывается (к нулю)
                    quotient = abs(value) // abs(divisor)
                    quotient = quotient if (value < 0) == (divisor < 0) else -quotient
                    value = self.check_int(quotient, op.line)  # INT_MIN / (0-1) не влезает в int
            else:
                self.putback()
                return value

    def factor(self, ex: bool) -> int:
        """Фактор => Переменная | Число | '(' Выражение ')'"""
        tok = self.get_token()
        match tok.code:
            case Tok.NUMBER | Tok.IDENT if not ex:
                return 0  # при разборе вхолостую значения не нужны, переполнения тоже не будет
            case Tok.NUMBER:
                return int(tok.value or 0)
            case Tok.IDENT:
                # переменная, которой ещё не было, заводится в таблице со значением 0
                return self.variables.setdefault(str(tok.value), 0)
            case Tok.LPAREN:
                value = self.expression(ex)
                self.expect(Tok.RPAREN, "')'")
                return value
            case _:
                raise CbasError(tok.line, "ожидалось число, переменная или '(', "
                                          f"а встретилось {describe(tok)}")

    # ---------- вспомогательное ----------

    def check_int(self, value: int, line: int) -> int:
        """Все переменные — int, поэтому результат должен влезать в 32 бита."""
        if not INT_MIN <= value <= INT_MAX:
            raise CbasError(line, f"переполнение int: результат {value} не помещается в 32 бита",
                            runtime=True)
        return value

    def read_int(self, line: int) -> int:
        """Ждёт, пока пользователь не введёт целое число. Числа можно вводить и по одному
        в строке, и несколько через пробел."""
        self.stdout.flush()  # чтобы подсказка из print появилась до ожидания ввода
        while True:
            if not self.input_words:
                text = self.stdin.readline()
                if text == "":
                    raise CbasError(line, "scan: ввод закончился, а число так и не введено",
                                    runtime=True)
                self.input_words = text.split()
                continue
            word = self.input_words.pop(0)
            if INT_RE.fullmatch(word) and INT_MIN <= int(word) <= INT_MAX:
                return int(word)
            print(f"scan: '{word}' — не целое число типа int, введите ещё раз",
                  file=self.stderr, flush=True)
