#!/usr/bin/env python3
"""Процессор языка разметки eMark (ТАЯК, ЛР6).

Читает документ eMark и выводит на консоль 24x80 отформатированный текст
или список ошибок. Обработка идёт в четыре этапа:
  1) лексер режет текст на токены: открывающий тег, закрывающий тег, текст;
  2) парсер собирает из токенов дерево и проверяет парность тегов;
  3) раскладка проходит по дереву, проверяет атрибуты, количество column/row
     и размеры, и сразу рисует ячейки в буфер экрана;
  4) буфер печатается с ANSI-цветами или без них.

Запуск: python3 main.py [--no-color] [--frame] документ.emark
"""

import sys
from bisect import bisect_right
from dataclasses import dataclass, field

SCREEN_H, SCREEN_W = 24, 80

# Какие атрибуты разрешены у каждого тега. Всё остальное — ошибка.
ATTRS = {
    "block": {"rows", "columns"},
    "column": {"valign", "halign", "textcolor", "bgcolor", "width"},
    "row": {"valign", "halign", "textcolor", "bgcolor", "height"},
}
VALIGN = ("top", "center", "bottom")
HALIGN = ("left", "center", "right")

# Значения по умолчанию из п. 4 ограничений. Вложенные ячейки берут
# невыставленные атрибуты у родительской ячейки, а не отсюда.
DEFAULT_STYLE = {"valign": "top", "halign": "left", "textcolor": 15, "bgcolor": 0}

# Цвета 0..15 нумеруются как в текстовом режиме PC (CGA): 0 чёрный, 1 синий,
# 2 зелёный, 3 бирюзовый, 4 красный, 5 пурпурный, 6 коричневый, 7 светло-серый,
# 8..15 — те же, но яркие (15 — белый). В ANSI порядок другой (1 — красный,
# 4 — синий), поэтому младшие три бита переставляем по таблице.
CGA_TO_ANSI = [0, 4, 2, 6, 1, 5, 3, 7]


@dataclass
class Token:
    kind: str           # "open", "close" или "text"
    value: str          # имя тега или сам текст
    line: int
    col: int
    attrs: dict = field(default_factory=dict)   # имя -> (значение, строка, столбец)


@dataclass
class Node:
    tag: str
    attrs: dict
    line: int
    col: int
    children: list = field(default_factory=list)
    text: str = ""


class Problems:
    """Копилка ошибок и предупреждений: (строка, столбец, вид, сообщение)."""

    def __init__(self):
        self.items = []

    def add(self, line, col, kind, message):
        self.items.append((line, col, kind, message))

    def has_errors(self):
        return any(kind != "предупреждение" for _, _, kind, _ in self.items)


# ---------------------------------------------------------------- лексер

def tokenize(src, problems):
    # Номер строки и столбца по индексу символа: ищем двоичным поиском,
    # в какую строку попадает индекс.
    starts = [0] + [i + 1 for i, c in enumerate(src) if c == "\n"]

    def pos(i):
        line = bisect_right(starts, i)
        return line, i - starts[line - 1] + 1

    def error(i, message):
        problems.add(*pos(i), "лексическая ошибка", message)

    tokens = []
    i, n = 0, len(src)
    while i < n:
        # Всё до следующего '<' — текст.
        if src[i] != "<":
            j = src.find("<", i)
            j = n if j == -1 else j
            # позиция текста — по первому непробельному символу, чтобы
            # сообщение об ошибке указывало на сам текст, а не на отступ
            k = i
            while k < j - 1 and src[k].isspace():
                k += 1
            tokens.append(Token("text", src[i:j], *pos(k)))
            i = j
            continue

        start = i
        i += 1
        closing = i < n and src[i] == "/"
        if closing:
            i += 1
        j = i
        while j < n and src[j].isalpha():
            j += 1
        name = src[i:j]
        i = j
        if not name:
            error(start, "после '<' ожидается имя тега")
            i = skip_to_gt(src, i)
            continue

        attrs, broken = {}, False
        while True:
            while i < n and src[i].isspace():
                i += 1
            if i >= n:
                error(start, f"тег <{'/' if closing else ''}{name}> не закрыт символом '>'")
                broken = True
                break
            if src[i] == ">":
                i += 1
                break
            if closing:
                error(i, f"у закрывающего тега </{name}> не бывает атрибутов")
                i, broken = skip_to_gt(src, i), True
                break

            # атрибут: имя = значение
            a = i
            while i < n and src[i].isalpha():
                i += 1
            attr = src[a:i]
            if not attr:
                error(i, f"неожиданный символ {src[i]!r} внутри тега <{name}>")
                i, broken = skip_to_gt(src, i), True
                break
            while i < n and src[i].isspace():
                i += 1
            if i >= n or src[i] != "=":
                error(a, f"после атрибута {attr} ожидается '='")
                i, broken = skip_to_gt(src, i), True
                break
            i += 1
            while i < n and src[i].isspace():
                i += 1
            if i < n and src[i] in "\"'":
                # значение в кавычках: rows="2"
                quote = src[i]
                end = src.find(quote, i + 1)
                if end == -1:
                    error(i, f"не закрыта кавычка в значении атрибута {attr}")
                    i, broken = n, True
                    break
                value, i = src[i + 1:end], end + 1
            else:
                v = i
                while i < n and not src[i].isspace() and src[i] not in "<>":
                    i += 1
                value = src[v:i]
            if not value:
                error(a, f"у атрибута {attr} нет значения")
                i, broken = skip_to_gt(src, i), True
                break
            if attr in attrs:
                error(a, f"атрибут {attr} указан повторно")
            attrs[attr] = (value, *pos(a))

        if not broken:
            tokens.append(Token("close" if closing else "open", name, *pos(start), attrs))
    return tokens


def skip_to_gt(src, i):
    """Восстановление после ошибки в теге: пропускаем всё до '>'."""
    j = src.find(">", i)
    return len(src) if j == -1 else j + 1


# ---------------------------------------------------------------- парсер

def parse(tokens, problems):
    """Строит дерево. Возвращает список блоков верхнего уровня или None,
    если парность тегов нарушена (тогда дерево строить дальше бессмысленно)."""

    def error(line, col, message):
        problems.add(line, col, "синтаксическая ошибка", message)

    root = Node("документ", {}, 1, 1)
    stack = [root]
    for t in tokens:
        top = stack[-1]
        if t.kind == "text":
            words = t.value.split()
            if not words:
                continue          # пробелы и переводы строк между тегами
            if top is root:
                error(t.line, t.col, "текст вне тегов: документ должен состоять из <block>")
            elif top.tag == "block":
                error(t.line, t.col, "текст прямо внутри <block>: он должен быть в <column> или <row>")
            else:
                # Пробельные символы сворачиваем в один пробел, как в HTML.
                top.text = " ".join(words)
            continue

        if t.value not in ATTRS:
            error(t.line, t.col, f"неизвестный тег <{'/' if t.kind == 'close' else ''}{t.value}>")
            return None

        if t.kind == "open":
            node = Node(t.value, t.attrs, t.line, t.col)
            top.children.append(node)
            stack.append(node)
        elif top is root:
            error(t.line, t.col, f"закрывающий тег </{t.value}> без открывающего")
            return None
        elif top.tag != t.value:
            error(t.line, t.col, f"закрывающий тег </{t.value}> не соответствует "
                                 f"открытому <{top.tag}> ({top.line}:{top.col})")
            return None
        else:
            stack.pop()

    if len(stack) > 1:
        node = stack[-1]
        error(node.line, node.col, f"тег <{node.tag}> не закрыт")
        return None
    if not root.children:
        error(1, 1, "документ должен содержать хотя бы один тег <block>")
        return None
    for node in root.children:
        if node.tag != "block":
            error(node.line, node.col, f"на верхнем уровне допускается только <block>, а не <{node.tag}>")
    return root.children


# ---------------------------------------------------------------- раскладка

class Layout:
    """Проверяет дерево и рисует его в буфер экрана. Размеры известны только
    при раскладке (блок занимает ячейку родителя), поэтому проверки размеров
    и количества тегов идут здесь же."""

    def __init__(self, problems):
        self.problems = problems
        # Буфер: для каждой клетки [символ, цвет текста, цвет фона].
        self.screen = [[[" ", 15, 0] for _ in range(SCREEN_W)] for _ in range(SCREEN_H)]

    def error(self, node, message):
        self.problems.add(node.line, node.col, "семантическая ошибка", message)

    def read_attrs(self, node):
        """Проверяет атрибуты тега и переводит значения в нужный тип.
        Неправильные атрибуты в результат не попадают."""
        out = {}
        for name, (value, line, col) in node.attrs.items():
            def bad(message):
                self.problems.add(line, col, "семантическая ошибка", message)

            if name not in ATTRS[node.tag]:
                bad(f"у тега <{node.tag}> нет атрибута {name}")
            elif name in ("valign", "halign"):
                allowed = VALIGN if name == "valign" else HALIGN
                if value in allowed:
                    out[name] = value
                else:
                    bad(f"{name}={value}: допустимы только {', '.join(allowed)}")
            elif not (value.isascii() and value.isdigit()):
                bad(f"{name}={value}: ожидается целое неотрицательное число")
            elif name in ("textcolor", "bgcolor") and int(value) > 15:
                bad(f"{name}={value}: цвет должен быть от 0 до 15")
            elif name in ("width", "height") and int(value) == 0:
                bad(f"{name}=0: размер должен быть больше нуля")
            else:
                out[name] = int(value)
        return out

    def place_block(self, block, x, y, w, h, style, top_level):
        """Блок занимает всю ячейку родителя: прямоугольник x, y, w, h."""
        a = self.read_attrs(block)
        for name in ("rows", "columns"):
            if name in block.attrs and name not in a:
                return            # значение неправильное, ошибка уже выдана
            if name not in a and not top_level:
                self.error(block, f"у вложенного <block> обязателен атрибут {name}")
                return
        # Умолчания columns=1, rows=0 — только для внешнего блока.
        rows, cols = a.get("rows", 0), a.get("columns", 1)

        ok = True
        if rows > h:
            self.error(block, f"rows={rows} больше высоты родителя ({h})")
            ok = False
        if cols > w:
            self.error(block, f"columns={cols} больше ширины родителя ({w})")
            ok = False
        if rows == 0 and cols == 0:
            self.error(block, "rows=0 и columns=0: в блоке нет ни строк, ни столбцов")
            ok = False
        if not ok:
            return

        if rows == 0:
            # Блок делится только на столбцы, каждый во всю высоту блока.
            columns = self.expect(block, "column", cols, f"в <block> с rows=0 ожидается {cols} <column>")
            if columns is not None:
                self.place_columns(columns, x, y, w, h, style)
            return

        # Блок делится на строки; если columns > 0, каждая строка — на столбцы.
        rows_list = self.expect(block, "row", rows, f"в <block> с rows={rows} ожидается {rows} <row>")
        if rows_list is None:
            return
        parts = self.split(rows_list, "height", h)
        if parts is None:
            return
        for row, ra, off, size in parts:            # ЦИКЛ по строкам блока
            if cols == 0:
                self.place_cell(row, ra, x, y + off, w, size, style)
                continue
            rst = merge(style, ra)
            self.fill(x, y + off, w, size, rst)
            if row.text:
                self.error(row, f"в блоке columns={cols} строка должна состоять из <column>, а не из текста")
            columns = self.expect(row, "column", cols, f"блок columns={cols}: в каждой <row> ожидается {cols} <column>")
            if columns is not None:
                self.place_columns(columns, x, y + off, w, size, rst)

    def expect(self, parent, tag, count, message):
        """Проверяет, что у parent ровно count детей и все они — <tag>.
        Возвращает подходящих детей даже при ошибке: экран всё равно не
        выведется, зато проверка дойдёт до вложенных тегов."""
        for child in parent.children:
            if child.tag != tag:
                self.error(child, f"{message}, а встретился <{child.tag}>")
        found = [child for child in parent.children if child.tag == tag]
        if len(found) != count:
            self.error(parent, f"{message}, а найдено {len(found)}")
        return found or None

    def split(self, nodes, size_name, total):
        """Делит длину total между столбцами (по width) или строками (по height).
        Размер обязателен у всех, кроме последнего: тому достаётся остаток."""
        parts, offset, ok = [], 0, True
        for i, node in enumerate(nodes):
            a = self.read_attrs(node)
            last = i == len(nodes) - 1
            if size_name in a:
                size = a[size_name]
            elif size_name in node.attrs:
                ok = False        # значение неправильное, ошибка уже выдана
                continue
            elif not last:
                self.error(node, f"у <{node.tag}> обязателен {size_name}: "
                                 f"по умолчанию он считается только для последнего")
                ok = False
                continue
            else:
                size = total - offset
                if size <= 0:
                    self.error(node, f"для последнего <{node.tag}> не осталось места: "
                                     f"предыдущие уже заняли {offset} из {total}")
                    ok = False
                    continue
            if offset + size > total:   # РАЗВИЛКА: не влезает в родителя
                self.error(node, f"{size_name}={size} не помещается: занято {offset} из {total}")
                ok = False
            parts.append((node, a, offset, size))
            offset += size
        return parts if ok else None

    def place_columns(self, columns, x, y, w, h, style):
        parts = self.split(columns, "width", w)
        if parts is None:
            return
        for col, ca, off, size in parts:             # ЦИКЛ по столбцам
            self.place_cell(col, ca, x + off, y, size, h, style)

    def place_cell(self, node, attrs, x, y, w, h, style):
        """Ячейка (column или row) с текстом или одним вложенным блоком."""
        st = merge(style, attrs)
        self.fill(x, y, w, h, st)
        if not node.children:
            self.draw_text(node, x, y, w, h, st)
        elif node.text:
            self.error(node, f"в <{node.tag}> нельзя одновременно писать текст и вложенные теги")
        elif len(node.children) != 1 or node.children[0].tag != "block":
            self.error(node, f"внутри <{node.tag}> допускается текст или ровно один <block>")
        else:
            self.place_block(node.children[0], x, y, w, h, st, top_level=False)

    def fill(self, x, y, w, h, st):
        for r in range(y, y + h):
            for c in range(x, x + w):
                self.screen[r][c] = [" ", st["textcolor"], st["bgcolor"]]

    def draw_text(self, node, x, y, w, h, st):
        lines = wrap(node.text, w)
        if len(lines) > h:
            self.problems.add(node.line, node.col, "предупреждение",
                              f"текст не поместился в <{node.tag}> {w}x{h}, "
                              f"отброшено строк: {len(lines) - h}")
            lines = lines[:h]
        top = {"top": 0, "center": (h - len(lines)) // 2, "bottom": h - len(lines)}[st["valign"]]
        for k, line in enumerate(lines):
            left = {"left": 0, "center": (w - len(line)) // 2, "right": w - len(line)}[st["halign"]]
            for j, ch in enumerate(line):
                self.screen[y + top + k][x + left + j][0] = ch


def merge(style, attrs):
    """Стиль ячейки: свои атрибуты, а чего нет — от родителя."""
    return {k: attrs.get(k, style[k]) for k in DEFAULT_STYLE}


def wrap(text, width):
    """Перенос по словам. Слово длиннее ширины ячейки режется на куски."""
    lines, cur = [], ""
    for word in text.split():
        while len(word) > width:                     # ЦИКЛ: режем длинное слово
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:width])
            word = word[width:]
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:      # РАЗВИЛКА: влезает в строку?
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- вывод

def sgr(fg, bg):
    """ANSI-последовательность для пары цветов (яркие — коды 90+/100+)."""
    f = (30 if fg < 8 else 90) + CGA_TO_ANSI[fg % 8]
    b = (40 if bg < 8 else 100) + CGA_TO_ANSI[bg % 8]
    return f"\x1b[{f};{b}m"


def render(screen, color, frame):
    out = []
    for row in screen:
        if color:
            s, cur = "", None
            for ch, fg, bg in row:
                if (fg, bg) != cur:      # escape-код только при смене цвета
                    s += sgr(fg, bg)
                    cur = (fg, bg)
                s += ch
            s += "\x1b[0m"
        else:
            s = "".join(cell[0] for cell in row)
            if not frame:
                s = s.rstrip()
        out.append(f"|{s}|" if frame else s)
    if frame:
        border = "+" + "-" * SCREEN_W + "+"
        out = [border] + out + [border]
    return "\n".join(out)


def process(src):
    """Весь конвейер: текст документа -> (список экранов, проблемы)."""
    problems = Problems()
    tokens = tokenize(src, problems)
    if problems.has_errors():
        return [], problems
    blocks = parse(tokens, problems)
    if blocks is None:
        return [], problems
    # Даже если парсер нашёл текст не на своём месте, дерево целое —
    # проверяем его дальше, чтобы показать сразу все ошибки.
    screens = []
    for block in blocks:          # каждый блок верхнего уровня — отдельный экран
        if block.tag != "block":
            continue
        layout = Layout(problems)
        try:
            layout.place_block(block, 0, 0, SCREEN_W, SCREEN_H, DEFAULT_STYLE, top_level=True)
        except RecursionError:
            # раскладка рекурсивная: сотни вложенных блоков упираются в стек Python
            problems.add(block.line, block.col, "семантическая ошибка",
                         "слишком глубокая вложенность блоков")
        screens.append(layout.screen)
    return ([] if problems.has_errors() else screens), problems


def main(argv):
    flags = {a for a in argv[1:] if a.startswith("--")}
    files = [a for a in argv[1:] if not a.startswith("--")]
    if flags - {"--no-color", "--frame"} or len(files) != 1:
        print("использование: python3 main.py [--no-color] [--frame] документ.emark", file=sys.stderr)
        return 2
    path = files[0]
    try:
        # utf-8-sig: файл из Блокнота начинается с BOM, его не надо считать текстом
        with open(path, encoding="utf-8-sig") as f:
            src = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"{path}: не удалось прочитать файл: {e}", file=sys.stderr)
        return 2

    # Python по умолчанию не переводит в int строки длиннее 4300 цифр;
    # снимаем ограничение, чтобы rows=999...9 дал ошибку размера, а не трейсбек.
    sys.set_int_max_str_digits(0)
    screens, problems = process(src)
    for screen in screens:
        print(render(screen, "--no-color" not in flags, "--frame" in flags))
    for line, col, kind, message in sorted(problems.items, key=lambda p: (p[0], p[1])):
        print(f"{path}:{line}:{col}: {kind}: {message}", file=sys.stderr)
    return 1 if problems.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
