"""Лексический анализатор C-light (порт cpp/lexer.hpp).

В грамматике из методички есть два уровня. <identifier>, <number>, <character>,
<digit>, <id_end>, <number_end> записаны через конкатенацию без пробелов
(<N1><N2>) и задают регулярные множества строк: это работа лексера (конечного
автомата), а не LL(1)-анализатора. Остальные правила записаны через пробельные
символы (<N1>   <N2>) и работают уже с токенами — их разбирает parser.py.

Лексер превращает текст в поток токенов с позициями и сам находит лексические
ошибки. После лексической ошибки он не останавливается: недопустимый символ
выбрасывается, а «испорченный» идентификатор или число всё равно выдаётся
токеном id/num, чтобы синтаксический анализ продолжался без лишних ошибок.

Как и в C++, исходник читается как байты: столбец считается в символах UTF-8,
а текст токенов переводится в str через surrogateescape, чтобы даже битый UTF-8
вернулся в вывод теми же байтами.
"""

from dataclasses import dataclass, field


def text_of(b: bytes) -> str:
    """Байты исходника → str без потерь (обратно — encode(..., 'surrogateescape'))."""
    return b.decode("utf-8", "surrogateescape")


@dataclass
class Token:
    """Токен. kind — имя терминала грамматики ("int", "id", "num", "(", "==", "$"),
    text — как он записан в исходнике. line/col — начало токена (с единицы),
    end_line/end_col — позиция сразу за ним: туда указываем, когда сообщаем
    «пропущена ';'», чтобы стрелка стояла после предыдущего токена, как в gcc."""
    kind: str = ""
    text: str = ""
    line: int = 1
    col: int = 1
    end_line: int = 1
    end_col: int = 1


@dataclass
class Diagnostic:
    """Сообщение об ошибке, общее для лексера и парсера."""
    line: int
    col: int
    category: str            # "лексическая" или "синтаксическая"
    type: str                # тип ошибки (см. README, раздел «Типы ошибок»)
    message: str             # понятное пояснение
    skipped: list[str] = field(default_factory=list)  # токены, пропущенные при восстановлении


# Ключевые слова зарезервированы, как в C: по символьной грамматике слово "int"
# подходит и под <identifier>, но тогда "int int = 5" стало бы неоднозначным.
# 'main' тоже считаем ключевым словом — в <program> он стоит как терминал.
KEYWORDS = {"int", "bool", "void", "main", "for", "if", "return"}

WHITESPACE = b" \t\n\r\v\f"


def is_letter(c: int) -> bool:
    return ord("a") <= c <= ord("z") or ord("A") <= c <= ord("Z") or c == ord("_")


def is_digit(c: int) -> bool:
    return ord("0") <= c <= ord("9")


class Lexer:
    def __init__(self, source: bytes):
        self.s = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self, k: int = 0) -> int:
        """Байт на позиции pos + k или 0 за концом входа (как '\\0' в C++)."""
        return self.s[self.pos + k] if self.pos + k < len(self.s) else 0

    def advance(self) -> None:
        """Сдвиг на один байт. Столбец считаем в символах, а не в байтах:
        байты-продолжения UTF-8 (10xxxxxx) столбец не увеличивают."""
        c = self.s[self.pos]
        self.pos += 1
        if c == ord("\n"):
            self.line += 1
            self.col = 1
        elif c & 0xC0 != 0x80:
            self.col += 1

    def tokenize(self, errors: list[Diagnostic]) -> list[Token]:
        tokens = []

        def error(l, c, type_, msg):
            errors.append(Diagnostic(l, c, "лексическая", type_, msg))

        while self.pos < len(self.s):
            c = self.peek()

            # Пробельные символы — как в C. Комментарии в C тоже считаются
            # пробельными символами, поэтому // и /* */ просто пропускаем.
            if c in WHITESPACE:
                self.advance()
                continue
            if c == ord("/") and self.peek(1) == ord("/"):
                while self.pos < len(self.s) and self.peek() != ord("\n"):
                    self.advance()
                continue
            if c == ord("/") and self.peek(1) == ord("*"):
                l, cl = self.line, self.col
                self.advance()
                self.advance()
                closed = False
                while self.pos < len(self.s):  # ЦИКЛ до "*/" или конца файла
                    if self.peek() == ord("*") and self.peek(1) == ord("/"):
                        self.advance()
                        self.advance()
                        closed = True
                        break
                    self.advance()
                if not closed:
                    error(l, cl, "незакрытый комментарий", "комментарий '/*' не закрыт до конца файла")
                continue

            t = Token(line=self.line, col=self.col)

            if is_letter(c):
                # <identifier>: <character><id_end> — только буквы и '_'.
                # Читаем и цифры тоже, чтобы "x1" дал одну ошибку, а не две.
                start = self.pos
                has_digit = False
                while is_letter(self.peek()) or is_digit(self.peek()):
                    has_digit |= is_digit(self.peek())
                    self.advance()
                t.text = text_of(self.s[start:self.pos])
                t.kind = t.text if t.text in KEYWORDS else "id"
                if has_digit:
                    error(t.line, t.col, "неверный идентификатор",
                          f"'{t.text}': по грамматике C-light идентификатор состоит "
                          "только из букв и '_', цифры не допускаются")
            elif is_digit(c):
                # <number>: <digit><number_end> — только цифры.
                start = self.pos
                bad = False
                while is_letter(self.peek()) or is_digit(self.peek()):
                    bad |= not is_digit(self.peek())
                    self.advance()
                t.text = text_of(self.s[start:self.pos])
                t.kind = "num"
                if bad:
                    error(t.line, t.col, "неверное число", f"'{t.text}': число может содержать только цифры")
            elif c in b"(){};":
                t.text = t.kind = chr(c)
                self.advance()
            elif c == ord("="):  # '=' или '=='
                self.advance()
                if self.peek() == ord("="):
                    self.advance()
                    t.text = "=="
                else:
                    t.text = "="
                t.kind = t.text
            elif c in b"<>":
                # В C-light есть только '<' и '>'. "<=" и ">=" — частая ошибка
                # человека, пишущего на C: сообщаем и выдаём '<' / '>'.
                self.advance()
                t.text = t.kind = chr(c)
                if self.peek() == ord("="):
                    self.advance()
                    error(t.line, t.col, "неподдерживаемая операция",
                          f"операции '{chr(c)}=' нет в C-light (есть только <, >, ==, !=); "
                          f"считаем, что написано '{chr(c)}'")
            elif c == ord("!"):
                self.advance()
                t.text = t.kind = "!="
                if self.peek() == ord("="):
                    self.advance()
                else:
                    error(t.line, t.col, "неподдерживаемая операция",
                          "одиночный '!' (в C-light есть только '!='); считаем, что написано '!='")
            else:
                # Чужой символ (',', '+', '@', кириллица...). UTF-8 символ может
                # занимать несколько байт — забираем его целиком.
                start = self.pos
                self.advance()
                while self.pos < len(self.s) and self.s[self.pos] & 0xC0 == 0x80:
                    self.advance()
                error(t.line, t.col, "недопустимый символ",
                      f"символ '{text_of(self.s[start:self.pos])}' не входит в алфавит C-light, пропущен")
                continue
            t.end_line = self.line
            t.end_col = self.col
            tokens.append(t)

        # Маркер конца входа $, как в методичке.
        tokens.append(Token("$", "$", self.line, self.col, self.line, self.col))
        return tokens
