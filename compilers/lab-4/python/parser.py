"""Нерекурсивный предиктивный анализатор (рис. 1 методички): входной буфер,
стек, таблица M[A, a] (порт cpp/parser.hpp). Восстановление после ошибок:
  - режим паники (обязательный, по умолчанию);
  - режим фразы (дополнение, флаг --phrase): ошибочные ячейки таблицы
    (пустые и synch) обрабатываются процедурами, которые вставляют, удаляют или заменяют
    один токен, а там, где локальная правка не подходит, — та же паника.

Каждая конфигурация (стек, вход) и действие записываются в trace — из него
получается таблица «Стек / Вход / Примечание», как в примере 4.
"""

from dataclasses import dataclass

from grammar import EPS, Grammar
from lexer import Diagnostic, Token

# Токены, на которых удобно синхронизироваться: разделители и начала
# операторов. Если такой токен ждёт кто-то глубже в стеке, верхний
# терминал считаем пропущенным, а не выбрасываем полезный токен со входа.
STRONG_SYNC = {";", "}", ")", "{", "for", "if", "return", "int", "bool", "void", "$"}

# Человеческие имена нетерминалов для сообщений «ожидалось: ...».
NAMES = {
    "<program>": "программа",
    "<type>": "тип",
    "<statement>": "оператор",
    "<stmts>": "оператор или '}'",
    "<declaration>": "объявление",
    "<assign>": "инициализация или конец объявления",
    "<assign_end>": "значение",
    "<for>": "for",
    "<if>": "if",
    "<return>": "return",
    "<bool_expression>": "логическое выражение",
    "<relop>": "операция сравнения",
}


@dataclass
class TraceRow:
    stack: str
    input: str
    note: str


def show(t: str) -> str:
    if t == "id":
        return "идентификатор"
    if t == "num":
        return "число"
    if t == "$":
        return "конец файла"
    return f"'{t}'"


def show_gen(t: str) -> str:
    """Родительный падеж: «вместо числа»."""
    if t == "id":
        return "идентификатора"
    if t == "num":
        return "числа"
    return f"'{t}'"


def quote(t: str) -> str:
    return t if t in ("id", "num") else f"'{t}'"


def code(s: str) -> str:
    return f"`{s}`"


class Parser:
    def __init__(self, g: Grammar, tokens: list[Token], phrase: bool):
        self.g = g
        self.toks = tokens
        self.phrase = phrase           # False — режим паники, True — режим фразы
        self.trace: list[TraceRow] = []
        self.errors: list[Diagnostic] = []  # только синтаксические
        self.aborted = False           # сработала защита от зацикливания (не должна)
        self.stack: list[str] = []     # stack[-1] — вершина
        self.ip = 0
        # True — идёт восстановление после уже сообщённой ошибки. Пока анализатор
        # не примет хотя бы один токен, новые сообщения не выдаём (консервативная
        # стратегия из методички), иначе одна ошибка даёт лавину ложных.
        self.recovering = False

    def run(self) -> None:
        g, stack = self.g, self.stack
        stack[:] = ["$", g.start]
        self.ip = 0
        # Защита на всякий случай: каждое действие при ошибке снимает символ со
        # стека или съедает токен, поэтому разбор конечен, но лимит не мешает.
        limit = 100000 + 50 * len(self.toks)

        step = 0
        while True:  # ЦИКЛ repeat ... until X = $ из методички
            if step > limit:
                self.aborted = True
                break
            step += 1
            row = TraceRow(self.stack_text(), self.input_text(), "")
            X = stack[-1]
            a = self.toks[self.ip]

            if X == "$":
                if a.kind == "$":  # X = a = $ — успешное завершение
                    row.note = ("Разбор завершён, ошибок нет" if not self.errors
                                else f"Разбор завершён, синтаксических ошибок: {len(self.errors)}")
                    self.trace.append(row)
                    break
                # Стек пуст, а вход ещё есть: программа уже закончилась.
                row.note = self.report(a, "текст после конца программы",
                                       f"'{a.text}' после закрывающей '}}' функции main")
                row.note += f" → пропускаем '{a.text}'"
                self.skip()
            elif not g.is_nonterminal(X):
                if X == a.kind:  # X = a ≠ $ — снимаем X, сдвигаем вход
                    row.note = f"совпадение '{a.text}'"
                    stack.pop()
                    self.ip += 1
                    self.recovering = False  # восстановление закончено: токен принят
                else:
                    row.note = self.phrase_terminal(X, a) if self.phrase else self.panic_terminal(X, a)
            else:
                k = g.cell(X, a.kind)
                if k >= 0:  # M[X,a] = X → Y1..Yk: заменяем X на Yk..Y1
                    stack.pop()
                    stack.extend(reversed(g.prods[k].rhs))
                    row.note = f"`{g.production_text(k)}`"
                elif (d := self.default_production(X, a.kind)) >= 0:
                    # Пустая ячейка, но у X есть продукция по умолчанию: раскрываем её,
                    # ошибку обнаружит её первый символ <type>. Так "main() {...}" без
                    # типа даёт одну ошибку «нет типа», а не пропуск всей программы.
                    stack.pop()
                    stack.extend(reversed(g.prods[d].rhs))
                    row.note = (f"`M[{X}, {a.kind}]` пусто, у {code(X)}"
                                f" одна продукция — раскрываем её по умолчанию: `{g.production_text(d)}`")
                else:
                    row.note = self.phrase_nonterminal(X, a) if self.phrase else self.panic_nonterminal(X, a)
            self.trace.append(row)

    # ---------- Режим паники ----------

    def panic_terminal(self, t: str, a: Token) -> str:
        """На вершине терминал t, на входе другой токен a."""
        if a.kind == "$":  # вход кончился — пропускать нечего, снимаем t
            n = self.report(a, "неожиданный конец файла", "ожидалось: " + show(t))
            self.stack.pop()
            return f"{n} → снимаем {quote(t)} со стека"
        if self.insertable(a.kind):  # РАЗВИЛКА: a подходит после t — значит, t пропущен
            n = self.report_missing(t, a)
            self.stack.pop()
            return f"{n} → снимаем {quote(t)} со стека"
        n = self.report(a, "неожиданный символ", f"'{a.text}', ожидалось: {show(t)}{self.block_hint(t, a.kind)}")
        self.skip()
        return f"{n} → пропускаем '{a.text}'"

    def panic_nonterminal(self, A: str, a: Token) -> str:
        """На вершине нетерминал A, ячейка M[A,a] пуста или synch."""
        cell_name = f"M[{A}, {a.kind}]"
        if a.kind == "$" or a.kind in self.g.synch[A]:  # РАЗВИЛКА: synch — снимаем A
            if a.kind == "$":
                n = self.report(a, "неожиданный конец файла", "ожидалось: " + self.describe(A))
            else:
                n = self.report(a, "неполная конструкция", f"перед '{a.text}' ожидалось: {self.describe(A)}")
            self.stack.pop()
            return f"{n}, `{cell_name}` = synch → {code(A)} снимается со стека"
        # Пустая ячейка — пропускаем входной символ.
        n = self.report(a, "неожиданный символ", f"'{a.text}', ожидалось: {self.describe(A)}")
        self.skip()
        return f"{n}, `{cell_name}` пусто → пропускаем '{a.text}'"

    # ---------- Режим фразы ----------
    # Локальные правки одного токена. Каждая правка снимает символ со стека
    # или съедает токен (кроме «вставки типа», после которой следующий шаг
    # гарантированно съедает id), поэтому зациклиться анализатор не может.

    def phrase_terminal(self, t: str, a: Token) -> str:
        b = self.next().kind
        if a.kind != "$" and b == t:  # РАЗВИЛКА: удаление — за a стоит ожидаемый t
            n = self.report(a, "лишний символ", f"'{a.text}' лишний, ожидаемый токен ({show(t)}) идёт следом")
            self.skip()
            return f"{n} → удаляем '{a.text}'"
        if a.kind == "$" or self.insertable(a.kind):  # РАЗВИЛКА: вставка t
            n = (self.report(a, "неожиданный конец файла", "ожидалось: " + show(t)) if a.kind == "$"
                 else self.report_missing(t, a))
            self.stack.pop()
            return f"{n} → вставляем {quote(t)}"
        if b in self.first_below():  # РАЗВИЛКА: замена — a стоит на месте t
            n = self.report(a, "замена символа", f"'{a.text}' вместо {show_gen(t)}{self.block_hint(t, a.kind)}")
            self.stack.pop()
            self.ip += 1  # токен не выброшен, а исправлен — в «пропущенные» не пишем
            return f"{n} → заменяем '{a.text}' на {quote(t)}"
        return self.panic_terminal(t, a)  # локальная правка не подошла

    def phrase_nonterminal(self, A: str, a: Token) -> str:
        b = self.next().kind
        stack = self.stack
        # Процедура для M[<relop>, =]: типичная ошибка «= вместо ==».
        if A == "<relop>" and a.kind == "=":
            n = self.report(a, "замена символа", "в сравнении '=' вместо '=='")
            stack.pop()
            self.ip += 1
            return n + " → заменяем '=' на '=='"
        # Процедура для M[<type>, id], если дальше снова id: "x i = 0" —
        # вместо типа написано неизвестное слово. Заменяем его на тип.
        if A == "<type>" and a.kind == "id" and b == "id":
            n = self.report(a, "неизвестный тип", f"'{a.text}' не является типом C-light (int, bool, void)")
            stack.pop()
            self.ip += 1
            return f"{n} → считаем '{a.text}' типом"
        # Процедуры для M[<statement>, id] (и <stmts>): оператор начинается с
        # идентификатора — это объявление, у которого испорчен тип:
        #   "x = 5;"     — тип пропущен, вставляем его;
        #   "float f;"   — неизвестный тип, заменяем его.
        # В обоих случаях дальше разбираем как "<тип> id <assign> ;".
        if A in ("<statement>", "<stmts>") and a.kind == "id" and b in ("=", ";", "id"):
            unknown_type = b == "id"
            if unknown_type:
                n = self.report(a, "неизвестный тип", f"'{a.text}' не является типом C-light (int, bool, void)")
            else:
                n = self.report(a, "объявление без типа", f"перед '{a.text}' не указан тип (int, bool или void)")
            stack.pop()
            if A == "<stmts>":
                stack.append("<stmts>")
            stack.extend([";", "<assign>", "id"])  # следующим шагом id совпадёт с токеном
            if unknown_type:
                self.ip += 1  # неизвестный тип съедаем, как будто это int
            action = f" → считаем '{a.text}' типом" if unknown_type else " → вставляем тип"
            return n + action + ", разбираем как " + code("<declaration> ;")
        if a.kind != "$" and self.g.cell(A, b) >= 0:  # РАЗВИЛКА: удаление лишнего a
            n = self.report(a, "лишний символ", f"'{a.text}' лишний, ожидалось: {self.describe(A)}")
            self.skip()
            return f"{n} → удаляем '{a.text}'"
        return self.panic_nonterminal(A, a)

    # ---------- Вспомогательное ----------

    def default_production(self, A: str, a: str) -> int:
        """Продукция по умолчанию для пустой (не synch) ячейки M[A, a], или -1."""
        if a == "$" or a in self.g.synch[A]:
            return -1
        return self.g.default_production(A)

    def next(self) -> Token:
        return self.toks[self.ip + 1 if self.ip + 1 < len(self.toks) else self.ip]

    def skip(self) -> None:
        if self.recovering and self.errors:
            self.errors[-1].skipped.append(self.toks[self.ip].text)
        self.ip += 1

    def first_below(self) -> set[str]:
        """FIRST того, что лежит в стеке под вершиной (что может идти после верхнего символа)."""
        res = set()
        for s in reversed(self.stack[:-1]):  # ЦИКЛ от вершины вниз
            if s == "$" or not self.g.is_nonterminal(s):
                res.add(s)
                return res
            f = self.g.first[s]
            res |= f - {EPS}
            if EPS not in f:
                return res
        return res

    def insertable(self, a: str) -> bool:
        """Можно ли выбросить верхний терминал и продолжить с токеном a?
        Да, если a идёт сразу после него, или если a — сильный разделитель,
        который примет какой-то символ глубже в стеке."""
        if a in self.first_below():
            return True
        if a not in STRONG_SYNC:
            return False
        for s in reversed(self.stack[:-1]):
            if s == a:
                return True
            if self.g.is_nonterminal(s) and self.g.cell(s, a) >= 0:
                return True
        return False

    def report(self, at: Token, type_: str, msg: str) -> str:
        """Регистрирует ошибку. Если идёт восстановление после предыдущей,
        новая ошибка не заводится — только пометка в таблице хода разбора."""
        return self.report_at(at.line, at.col, type_, msg)

    def report_at(self, line: int, col: int, type_: str, msg: str) -> str:
        if self.recovering:
            return "восстановление"
        self.recovering = True
        self.errors.append(Diagnostic(line, col, "синтаксическая", type_, msg))
        return f"Ошибка {len(self.errors)} ({type_}: {msg})"

    def report_missing(self, t: str, a: Token) -> str:
        """«Пропущен символ» указываем сразу после предыдущего токена."""
        line, col = a.line, a.col
        if self.ip > 0:
            prev = self.toks[self.ip - 1]
            line, col = prev.end_line, prev.end_col
        return self.report_at(line, col, "пропущен символ", f"ожидалось: {show(t)} перед '{a.text}'")

    def block_hint(self, t: str, a: str) -> str:
        """Подсказка для исходной грамматики: в { } помещается ровно один оператор."""
        if self.g.ext or t != "}" or a not in self.g.first["<statement>"]:
            return ""
        return " (в C-light блок { } содержит ровно один оператор; последовательности — расширение --ext)"

    def describe(self, A: str) -> str:
        """Что ожидалось вместо нетерминала: человеческое имя + токены, для которых
        в строке M[A, ·] есть продукция."""
        lst = ", ".join(show(a) for a in self.g.terminals if self.g.cell(A, a) >= 0)
        return f"{NAMES.get(A, A)} ({lst})"

    def stack_text(self) -> str:
        """Стек как в методичке: дно $ слева, вершина справа."""
        return " ".join(self.stack)

    def input_text(self) -> str:
        """Остаток входа; длинный хвост сокращаем, чтобы таблица читалась."""
        max_shown = 10
        r = ""
        i = self.ip
        while i < len(self.toks) and self.toks[i].kind != "$" and i - self.ip < max_shown:
            r += self.toks[i].text + " "
            i += 1
        if self.toks[i].kind != "$":
            r += "… "
        return r + "$"
