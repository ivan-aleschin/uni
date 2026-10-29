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
    M[<init_rest>, ;] — «{1, 2;»: пропущена '}', вставляем её (снимаем <init_rest> и '}').
    M[<size>, id] — «int d[x]»: размер массива должен быть числом; считаем
      идентификатор размером (заменяем его на num) и разбираем дальше."""
    if A == "<init_rest>" and a.kind in ("id", "num"):
        n = p.report_missing(",", a)
        p.stack.pop()
        p.stack.extend(["<init_rest>", "<assign_end>"])
        return f"{n} → вставляем ','"
    if A == "<init_rest>" and a.kind == ";" and p.stack[-2] == "}":
        n = p.report_missing("}", a)
        p.stack.pop()
        p.stack.pop()
        return f"{n} → вставляем '}}'"
    if A == "<size>" and a.kind == "id" and b == "]":
        n = p.report(a, "неверный размер массива", f"'{a.text}': размер массива должен быть числом")
        p.stack.pop()
        p.ip += 1
        return f"{n} → считаем '{a.text}' размером"
    return None


def check_arrays(tokens: list[Token]) -> list[Diagnostic]:
    """Семантические проверки массивов. Грамматикой их не выразить: int a[0]
    и int a[5] синтаксически одинаковы. Идём по токенам, запоминаем объявления
    и проверяем каждое обращение. Проверки смотрят только на соседние токены,
    поэтому работают и в программе с синтаксическими ошибками. Области
    видимости не учитываются: имя относится к последнему объявлению выше."""
    errors = []
    sizes: dict[str, int | None] = {}   # массив → размер (None — неизвестен)
    scalars: set[str] = set()           # обычные переменные

    def error(t, type_, msg):
        errors.append(Diagnostic(t.line, t.col, "семантическая", type_, msg))

    def kind(j):
        return tokens[j].kind if j < len(tokens) else "$"

    def number(j):
        """Значение токена-числа на позиции j, если это правильное число, иначе None."""
        return int(tokens[j].text) if kind(j) == "num" and tokens[j].text.isdigit() else None

    i = 0
    while i < len(tokens):  # ЦИКЛ по токенам
        t = tokens[i]
        if t.kind in TYPES and kind(i + 1) == "id":
            # --- Объявление: <type> id ...
            name = tokens[i + 1].text
            i += 2
            if kind(i) != "[":  # РАЗВИЛКА: обычная переменная
                if kind(i) in ("=", ";"):  # сломанное объявление («int a 3];») не запоминаем
                    scalars.add(name)
                    sizes.pop(name, None)
                continue
            scalars.discard(name)
            # int name [ size ] = { v1 , v2 , ... }
            size = number(i + 1)
            if size == 0:
                error(tokens[i + 1], "неверный размер массива", f"размер массива '{name}' должен быть больше нуля")
            j = i + 1                  # за '[': шагаем через «num ]»; пропущенную ']' терпим (int a[3 = {...})
            if kind(j) == "num":
                j += 1
            if kind(j) == "]":
                j += 1
            count = None
            if kind(j) == "=" and kind(j + 1) == "{":
                # Значение — это id или num, кроме стоящих в индексе (a[1]: '1' идёт за '[').
                k = j + 2
                count = 0
                while kind(k) not in ("}", ";", "$"):
                    count += kind(k) in ("id", "num") and kind(k - 1) != "["
                    k += 1
                if size and count > size:
                    error(tokens[j], "слишком много инициализаторов",
                          f"размер массива '{name}' — {size}, а значений в списке — {count}")
            elif kind(i + 1) == "]" and kind(j) != "=":  # «int a[] = 5;» — уже синтаксическая ошибка
                error(tokens[i - 1], "не указан размер массива",
                      f"у массива '{name}' нет ни размера, ни списка инициализации")
            sizes[name] = size or count or None   # 0 (ошибка уже выдана) — размер неизвестен
            continue
        if t.kind == "id":
            # --- Использование имени: name [ ... ] или просто name
            name = t.text
            if kind(i + 1) == "[":
                n = sizes.get(name)
                idx = number(i + 2) if kind(i + 3) == "]" else None
                if name in scalars:
                    error(t, "индексация не массива", f"'{name}' объявлена как переменная, а не массив")
                elif n is not None and idx is not None and idx >= n:
                    error(tokens[i + 2], "индекс за границами массива",
                          f"'{name}[{idx}]': допустимые индексы массива '{name}' — от 0 до {n - 1}")
            elif name in sizes:
                error(t, "массив без индекса",
                      f"'{name}' — массив, к нему можно обращаться только по индексу: {name}[i]")
        i += 1
    return errors
