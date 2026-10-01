"""Лексический анализатор CBAS: переводит лексемы из внешнего формата во внутренний.

Внешний формат — то, что написано в тексте программы ("for", "x", "12", "=="),
внутренний — номер лексемы (Tok). Дальше интерпретатор работает только с номерами.
"""

from dataclasses import dataclass
from enum import IntEnum
import string

INT_MIN = -(2**31)  # переменные CBAS — аналог int, т.е. 32 бита со знаком
INT_MAX = 2**31 - 1


class Tok(IntEnum):
    """Внутренние номера лексем. По диапазону номера сразу виден тип лексемы."""

    END = 0  # конец программы
    # 1..9 — ключевые слова
    PRINT = 1
    SCAN = 2
    FOR = 3
    TO = 4
    IF = 5
    ELSE = 6
    # 10..19 — лексемы со значением
    IDENT = 10  # переменная
    NUMBER = 11
    STRING = 12
    # 20.. — разделители и знаки операций
    PLUS = 20
    MINUS = 21
    MUL = 22
    DIV = 23
    LPAREN = 24
    RPAREN = 25
    LBRACE = 26
    RBRACE = 27
    ASSIGN = 28
    LT = 29
    GT = 30
    EQ = 31
    NE = 32
    COMMA = 33
    SEMI = 34


# Таблица ключевых слов (в методичке — struct commands table[])
KEYWORDS: dict[str, Tok] = {
    "print": Tok.PRINT,
    "scan": Tok.SCAN,
    "for": Tok.FOR,
    "to": Tok.TO,
    "if": Tok.IF,
    "else": Tok.ELSE,
}

# Таблица разделителей. Двухсимвольные проверяются раньше односимвольных
DELIMITERS: dict[str, Tok] = {
    "==": Tok.EQ,
    "!=": Tok.NE,
    "+": Tok.PLUS,
    "-": Tok.MINUS,
    "*": Tok.MUL,
    "/": Tok.DIV,
    "(": Tok.LPAREN,
    ")": Tok.RPAREN,
    "{": Tok.LBRACE,
    "}": Tok.RBRACE,
    "=": Tok.ASSIGN,
    "<": Tok.LT,
    ">": Tok.GT,
    ",": Tok.COMMA,
    ";": Tok.SEMI,
}

LETTERS = set(string.ascii_letters + "_")  # по спецификации: латинские буквы и '_'
DIGITS = set(string.digits)


def kind(code: Tok) -> str:
    """Тип лексемы — нужен анализатору, чтобы понять: число, переменная или операция."""
    if code == Tok.END:
        return "конец"
    if code < 10:
        return "ключевое слово"
    if code == Tok.IDENT:
        return "переменная"
    if code == Tok.NUMBER:
        return "число"
    if code == Tok.STRING:
        return "строка"
    return "разделитель"


@dataclass
class Token:
    code: Tok  # внутренний формат
    text: str  # внешний формат, нужен только для сообщений об ошибках
    value: int | str | None  # значение числа, текст строки или имя переменной
    line: int


class CbasError(Exception):
    """Ошибка в программе на CBAS: лексическая, синтаксическая или ошибка выполнения."""

    def __init__(self, line: int, message: str, runtime: bool = False) -> None:
        super().__init__(message)
        self.line = line
        self.message = message
        self.runtime = runtime

    def __str__(self) -> str:
        where = "Ошибка выполнения" if self.runtime else "Ошибка"
        return f"{where} в строке {self.line}: {self.message}"


class Lexer:
    def __init__(self, source: str) -> None:
        self.src = source
        self.pos = 0
        self.line = 1

    def get_token(self) -> Token:
        """Берёт из входного потока очередную лексему и возвращает её во внутреннем формате."""
        src = self.src
        # пропускаем пробелы и переводы строк, считая строки
        while self.pos < len(src) and src[self.pos].isspace():
            if src[self.pos] == "\n":
                self.line += 1
            self.pos += 1
        if self.pos >= len(src):
            return Token(Tok.END, "", None, self.line)

        start, line, ch = self.pos, self.line, src[self.pos]

        if ch in LETTERS:  # ключевое слово или переменная
            while self.pos < len(src) and src[self.pos] in LETTERS:
                self.pos += 1
            if self.pos < len(src) and src[self.pos] in DIGITS:
                word = self.take_word(start)
                raise CbasError(line, f"недопустимое имя '{word}': имя переменной состоит "
                                      "только из латинских букв и '_'")
            word = src[start:self.pos]
            code = KEYWORDS.get(word, Tok.IDENT)
            return Token(code, word, word if code == Tok.IDENT else None, line)

        if ch in DIGITS:  # число
            while self.pos < len(src) and src[self.pos] in DIGITS:
                self.pos += 1
            if self.pos < len(src) and src[self.pos] in LETTERS:
                raise CbasError(line, f"недопустимая лексема '{self.take_word(start)}'")
            text = src[start:self.pos]
            if int(text) > INT_MAX:
                raise CbasError(line, f"число {text} не помещается в int (максимум {INT_MAX})")
            return Token(Tok.NUMBER, text, int(text), line)

        if ch == '"':  # строка: любые символы, кроме кавычки
            end = src.find('"', self.pos + 1)
            if end == -1:
                raise CbasError(line, "строка не закрыта кавычкой '\"'")
            text = src[start:end + 1]
            self.line += text.count("\n")
            self.pos = end + 1
            return Token(Tok.STRING, text, text[1:-1], line)

        two = src[self.pos:self.pos + 2]
        if two in DELIMITERS:
            self.pos += 2
            return Token(DELIMITERS[two], two, None, line)
        if ch in DELIMITERS:
            self.pos += 1
            return Token(DELIMITERS[ch], ch, None, line)
        if ch == "!":
            raise CbasError(line, "после '!' ожидалось '=' (операция '!=')")
        raise CbasError(line, f"недопустимый символ '{ch}'")

    def take_word(self, start: int) -> str:
        """Дочитывает слово из букв и цифр целиком — чтобы показать его в сообщении об ошибке."""
        while self.pos < len(self.src) and (self.src[self.pos] in LETTERS or self.src[self.pos] in DIGITS):
            self.pos += 1
        return self.src[start:self.pos]


def tokenize(source: str) -> list[Token]:
    """Переводит весь текст во внутренний формат; последняя лексема — END."""
    lexer = Lexer(source)
    tokens = [lexer.get_token()]
    while tokens[-1].code != Tok.END:
        tokens.append(lexer.get_token())
    return tokens
