"""Дополнительное задание: массивы в C-light (флаг --arrays).

Что добавляется к расширенной грамматике (--ext, последовательность операторов в блоке):

  объявление и инициализация:   int a[3];   int a[3] = {1, x, 0};   int a[] = {1, 2};
  обращение к ячейке:            a[i], a[0] — справа от '=', в условиях if/for
  присваивание:                  a[i] = 5;   x = a[0];

Здесь три части:
  1. add_arrays — новые продукции грамматики. Таблица M, FIRST, FOLLOW и synch
     по ним строятся тем же build_tables, поэтому синтаксические ошибки в массивах
     (нет ']', нет ',' между значениями, незакрытая '{' …) находит и восстанавливает
     тот же анализатор в режиме паники или фразы;
  2. ArrayLexer — лексер, который знает символы '[', ']' и ',';
  3. check_arrays — семантические проверки, которых грамматика выразить не может:
     размер, число инициализаторов, индекс за границей, индексация не-массива,
     массив без индекса.
"""

from grammar import Grammar, Production
from lexer import Diagnostic, Lexer, Token
from parser import NAMES, PHRASE_PROCEDURES, Parser

TYPES = ("int", "bool", "void")


class ArrayLexer(Lexer):
    """Лексер C-light с тремя дополнительными односимвольными токенами."""
    punct = b"(){};[],"


def add_arrays(g: Grammar) -> None:
    """Дописывает в грамматику g (построенную make_grammar(ext=True)) продукции
    для массивов. Новые продукции ставятся сразу после продукций с той же
    левой частью, чтобы номера в таблице шли по порядку конструкций."""
    assert g.ext, "массивы добавляются к расширенной грамматике"
    g.arrays = True

    def replace(lhs, old, new):
        for p in g.prods:
            if p.lhs == lhs and p.rhs == old:
                p.rhs = new
                return
        raise ValueError(f"нет продукции {lhs} → {old}")

    def insert(lhs, rhs):
        # после последней продукции с той же левой частью, иначе — в конец
        pos = len(g.prods)
        for k, p in enumerate(g.prods):
            if p.lhs == lhs:
                pos = k + 1
        g.prods.insert(pos, Production(lhs, rhs))

    # Объявление: после имени — либо обычная инициализация, либо размер массива.
    replace("<declaration>", ["<type>", "id", "<assign>"], ["<type>", "id", "<decl_tail>"])
    insert("<decl_tail>", ["<assign>"])
    insert("<decl_tail>", ["[", "<size>", "]", "<array_init>"])
    insert("<size>", ["num"])
    insert("<size>", [])                     # int a[] = {...} — размер по числу значений
    insert("<array_init>", [])
    insert("<array_init>", ["=", "{", "<init_list>", "}"])
    insert("<init_list>", ["<assign_end>", "<init_rest>"])
    insert("<init_rest>", [",", "<assign_end>", "<init_rest>"])
    insert("<init_rest>", [])

    # Обращение к ячейке: после идентификатора может стоять [индекс].
    replace("<assign_end>", ["id"], ["id", "<index>"])
    replace("<bool_expression>", ["id", "<relop>", "id"], ["id", "<index>", "<relop>", "id", "<index>"])
    replace("<bool_expression>", ["num", "<relop>", "id"], ["num", "<relop>", "id", "<index>"])
    insert("<index>", [])
    insert("<index>", ["[", "<subscript>", "]"])
    insert("<subscript>", ["id"])
    insert("<subscript>", ["num"])

    # Присваивание ячейке или переменной — без него к ячейке нельзя записать значение.
    insert("<statement>", ["id", "<index>", "=", "<assign_end>", ";"])

    i = g.terminals.index("id")
    g.terminals[i:i] = ["[", "]", ","]
    for p in g.prods:
        if p.lhs not in g.first:
            g.nonterminals.append(p.lhs)
            g.first[p.lhs] = set()

    PHRASE_PROCEDURES[:] = [phrase_arrays]
    NAMES.update({
        "<decl_tail>": "размер массива или инициализация",
        "<size>": "размер массива",
        "<array_init>": "инициализация массива или конец объявления",
        "<init_list>": "значение",
        "<init_rest>": "продолжение списка значений",
        "<index>": "индекс или продолжение выражения",
        "<subscript>": "индекс",
    })


def phrase_arrays(p: Parser, A: str, a: Token, b: str) -> str | None:
    """Процедуры режима фразы для массивов (ячейки M[A, a] без продукции).

    M[<init_rest>, id/num] — «{1 2}»: между значениями пропущена ',', вставляем её:
      вместо <init_rest> кладём <init_rest> <assign_end>, и следующим шагом
      <assign_end> разбирает текущее значение — токен не теряется.
    M[<size>, id] — «int d[x]»: размер массива должен быть числом; считаем
      идентификатор размером (заменяем его на num) и разбираем дальше."""
    if A == "<init_rest>" and a.kind in ("id", "num"):
        n = p.report_missing(",", a)
        p.stack.pop()
        p.stack.extend(["<init_rest>", "<assign_end>"])
        return f"{n} → вставляем ','"
    if A == "<size>" and a.kind == "id" and b == "]":
        n = p.report(a, "неверный размер массива", f"'{a.text}': размер массива должен быть числом")
        p.stack.pop()
        p.ip += 1
        return f"{n} → считаем '{a.text}' размером"
    return None


def check_arrays(tokens: list[Token]) -> list[Diagnostic]:
    """Семантические проверки массивов по потоку токенов (после синтаксического разбора).

    Проверки сделаны по шаблонам токенов, а не по дереву: так они работают и в
    программе с синтаксическими ошибками, а каждая смотрит только на свою
    конструкцию. Области видимости не учитываются: имя относится к последнему
    объявлению выше по тексту (в C-light нет функций, кроме main)."""
    errors = []
    arrays: dict[str, int | None] = {}   # имя массива → размер (None — неизвестен)
    scalars: set[str] = set()

    def error(t, type_, msg):
        errors.append(Diagnostic(t.line, t.col, "семантическая", type_, msg))

    def kind(j):
        return tokens[j].kind if j < len(tokens) else "$"

    i = 0
    while i < len(tokens):  # ЦИКЛ по токенам
        t = tokens[i]
        # --- Объявление: <type> id ...
        if t.kind in TYPES and kind(i + 1) == "id":
            name_tok = tokens[i + 1]
            i += 2
            if kind(i) != "[":  # РАЗВИЛКА: обычная переменная
                scalars.add(name_tok.text)
                arrays.pop(name_tok.text, None)
                continue
            # int a [ N ] = { v1, v2 }
            size = None
            if kind(i + 1) == "num" and kind(i + 2) == "]":
                size = int(tokens[i + 1].text) if tokens[i + 1].text.isdigit() else None
                if size == 0:
                    error(tokens[i + 1], "неверный размер массива",
                          f"размер массива '{name_tok.text}' должен быть больше нуля")
                    size = None
            j = i + 1
            while kind(j) not in ("]", ";", "=", "$"):
                j += 1
            if kind(j) == "]":
                j += 1
            count = None
            if kind(j) == "=" and kind(j + 1) == "{":
                count, depth, k = 0, 0, j + 2
                had_value = False
                while kind(k) not in ("}", ";", "$"):  # ЦИКЛ по значениям инициализатора
                    if kind(k) == "[":
                        depth += 1
                    elif kind(k) == "]":
                        depth -= 1
                    elif kind(k) == "," and depth == 0:
                        count += had_value
                        had_value = False
                    elif kind(k) in ("id", "num") and depth == 0:
                        had_value = True
                    k += 1
                count += had_value
                if size is not None and count > size:
                    error(tokens[j], "слишком много инициализаторов",
                          f"размер массива '{name_tok.text}' — {size}, а значений в списке — {count}")
            no_size = not (kind(i + 1) == "num" and kind(i + 2) == "]")
            if no_size and kind(i + 1) == "]" and count is None:
                error(name_tok, "не указан размер массива",
                      f"у массива '{name_tok.text}' нет ни размера, ни списка инициализации")
            arrays[name_tok.text] = size if size is not None else count
            scalars.discard(name_tok.text)
            continue
        # --- Использование имени: id [ ... ] или просто id
        if t.kind == "id":
            name = t.text
            if kind(i + 1) == "[":
                if name in scalars:
                    error(t, "индексация не массива", f"'{name}' объявлена как переменная, а не массив")
                elif (n := arrays.get(name)) is not None and kind(i + 2) == "num" \
                        and kind(i + 3) == "]" and tokens[i + 2].text.isdigit():
                    idx = int(tokens[i + 2].text)
                    if idx >= n:
                        error(tokens[i + 2], "индекс за границами массива",
                              f"'{name}[{idx}]': допустимые индексы массива '{name}' — от 0 до {n - 1}")
            elif name in arrays:
                error(t, "массив без индекса",
                      f"'{name}' — массив, к нему можно обращаться только по индексу: {name}[i]")
        i += 1
    return errors
