"""ЛР4 по ТАЯК: синтаксический анализатор C-light, обнаруживающий наибольшее
число ошибок. Лексер → FIRST/FOLLOW → таблица M[A, a] → нерекурсивный
предиктивный анализатор со стеком и восстановлением после ошибок.
Результат — вывод в консоль и таблицы хода разбора в файлах .md.

Запуск:  python3 main.py [--phrase] [--ext] [--out DIR] файл.cl
         python3 main.py --table [--ext] [--out DIR]
  --phrase  восстановление в режиме фразы (по умолчанию — режим паники)
  --ext     расширенная грамматика: в { } последовательность операторов
  --out     куда писать таблицы (по умолчанию results/ рядом с main.py)
  --table   только построить таблицу предиктивного анализа

Файлы:  DIR/<имя>.trace.md         — ход разбора (как пример 4), режим паники
        DIR/<имя>.phrase.trace.md  — то же в режиме фразы
        DIR/parse_table.md (parse_table_ext.md) — FIRST, FOLLOW, synch, M[A, a]
Код возврата: 0 — ошибок нет, 1 — найдены ошибки, 2 — неверный запуск.
"""

import os
import sys

from grammar import EPS, Grammar, build_tables, make_grammar
from lexer import Diagnostic, Lexer, text_of
from parser import Parser


def to_bytes(s: str) -> bytes:
    """Обратно в байты; surrogateescape возвращает битые байты исходника как были."""
    return s.encode("utf-8", "surrogateescape")


def width(s: str) -> int:
    """Ширина строки в символах (байты UTF-8, кроме байтов-продолжений) —
    для выравнивания столбцов с кириллицей."""
    return sum(1 for c in to_bytes(s) if c & 0xC0 != 0x80)


def pad(s: str, w: int) -> str:
    return s + " " * max(w - width(s), 0)


def write_table(out: list[str], head: list[str], rows: list[list[str]]) -> None:
    """Markdown-таблица с выровненными столбцами: читается и на GitHub, и в обычном редакторе."""
    w = [max(3, width(h)) for h in head]
    for r in rows:
        for j, x in enumerate(r):
            w[j] = max(w[j], width(x))

    def line(r):
        out.append("|" + "".join(f" {pad(x, w[j])} |" for j, x in enumerate(r)) + "\n")

    line(head)
    out.append("|" + "".join("-" * (wj + 2) + "|" for wj in w) + "\n")
    for r in rows:
        line(r)


def join_set(s: set[str], order: list[str]) -> str:
    """Выводим в порядке столбцов таблицы, ε — в конце."""
    items = [t for t in order if t in s]
    if EPS in s:
        items.append(EPS)
    return " ".join(items)


def write_parse_table(g: Grammar, file: str) -> None:
    """Файл с грамматикой, FIRST/FOLLOW/synch и таблицей M[A, a]."""
    out = []
    out.append("# Таблица предиктивного анализа C-light" + (" (расширенная грамматика, --ext)" if g.ext else "")
               + "\n\nСгенерировано программой ЛР4 (`main.py`) по грамматике\n"
               "из `grammar.py`.\n"
               "Нетерминалы — в угловых скобках, `id` и `num` — токены лексера (`<identifier>` и `<number>`).\n\n")

    out.append("## Продукции\n\n```\n")
    for k in range(len(g.prods)):
        out.append(f"{k + 1:>2}. {g.production_text(k)}\n")
    out.append("```\n\n")

    out.append("## FIRST, FOLLOW и синхронизирующие множества\n\n")
    rows = [[f"`{A}`", f"`{join_set(g.first[A], g.terminals)}`",
             f"`{join_set(g.follow[A], g.terminals)}`", f"`{join_set(g.synch[A], g.terminals)}`"]
            for A in g.nonterminals]
    write_table(out, ["Нетерминал", "FIRST", "FOLLOW", "synch (режим паники)"], rows)

    out.append("\n## Таблица M[A, a]\n\n"
               "В ячейке — номер продукции из списка выше; `synch` — синхронизирующий символ "
               "(при ошибке нетерминал снимается со стека); пустая ячейка — ошибка, входной символ пропускается; "
               "`(k)` — ошибка, но у нетерминала единственная продукция k, начинающаяся с `<type>`; она "
               "раскрывается по умолчанию, и ошибку сообщает уже `<type>`.\n\n")
    head = ["A \\ a"] + [f"`{t}`" for t in g.terminals]
    rows = []
    for A in g.nonterminals:
        r = [f"`{A}`"]
        d = g.default_production(A)
        for t in g.terminals:
            k = g.cell(A, t)
            if k >= 0:
                r.append(str(k + 1))
            elif t in g.synch[A]:
                r.append("synch")
            elif d >= 0 and t != "$":
                r.append(f"({d + 1})")
            else:
                r.append("")
        rows.append(r)
    write_table(out, head, rows)

    out.append("\n## Проверка LL(1)\n\n")
    if not g.conflicts:
        out.append("Ни в одной ячейке нет двух продукций — грамматика LL(1).\n")
    for c in g.conflicts:
        out.append(f"- конфликт: {c}\n")

    out.append("\n## Режим фразы (--phrase)\n\n"
               "Ошибочные ячейки (пустые и synch) обрабатываются процедурами (проверяются по порядку):\n\n"
               "1. `M[<relop>, =]` — замена `=` на `==`;\n"
               "2. `M[<type>, id]`, если за ним снова id, — неизвестный тип, считаем его типом;\n"
               "3. `M[<statement>, id]` (и `M[<stmts>, id]`): если за id идёт `=` или `;` — объявление без типа,\n"
               "   если ещё один id — неизвестный тип; дальше разбираем как `id <assign> ;`;\n"
               "4. если следующий токен b подходит (`M[A, b]` не пусто) — текущий токен лишний, удаляем его;\n"
               "5. иначе — как в режиме паники (synch → снять A, пусто → пропустить токен).\n\n"
               "Несовпадение терминала t на вершине с токеном a: удаление a (если за ним идёт t), вставка t\n"
               "(если a может идти после t), замена a на t (если следующий токен может идти после t), иначе паника.\n")
    with open(file, "wb") as f:
        f.write(to_bytes("".join(out)))


def source_line(lines: list[bytes], line: int, col: int) -> str:
    """Строка исходника с номером и стрелкой под позицией ошибки (как в gcc)."""
    if line < 1 or line > len(lines):
        return ""
    l = lines[line - 1]
    prefix = str(line)
    r = f"  {prefix} | {text_of(l)}\n  {' ' * len(prefix)} | "
    # Стрелку ставим под col-м символом: табы копируем, остальное заменяем пробелами.
    c = 1
    for ch in l:
        if c >= col:
            break
        if ch & 0xC0 == 0x80:
            continue
        r += "\t" if ch == ord("\t") else " "
        c += 1
    return r + "^\n"


def main() -> int:
    argv = sys.argv
    phrase = ext = table_only = False
    # По умолчанию пишем в results/ рядом с main.py (а не в текущую папку),
    # так результат один и тот же, откуда бы ни запускали.
    out_dir = os.path.normpath(os.path.join(os.path.dirname(argv[0]), "results"))
    input_path = ""
    i = 1
    while i < len(argv):  # ЦИКЛ по аргументам командной строки
        a = argv[i]
        if a == "--phrase":
            phrase = True
        elif a == "--ext":
            ext = True
        elif a == "--table":
            table_only = True
        elif a == "--out" and i + 1 < len(argv):
            i += 1
            out_dir = argv[i]
        elif a and a[0] != "-" and not input_path:
            input_path = a
        else:
            print(f"неизвестный аргумент: {a}", file=sys.stderr)
            return 2
        i += 1
    if not table_only and not input_path:
        print(f"Использование: {argv[0]} [--phrase] [--ext] [--out DIR] файл.cl\n"
              f"               {argv[0]} --table [--ext] [--out DIR]", file=sys.stderr)
        return 2

    stdout = []  # всё, что идёт в консоль; пишем одним куском в конце, байтами

    def flush():
        sys.stdout.buffer.write(to_bytes("".join(stdout)))
        sys.stdout.buffer.flush()

    # 1. Грамматика → FIRST, FOLLOW, таблица M, synch.
    g = make_grammar(ext)
    build_tables(g)
    os.makedirs(out_dir, exist_ok=True)
    table_file = os.path.join(out_dir, "parse_table_ext.md" if ext else "parse_table.md")
    write_parse_table(g, table_file)
    if g.conflicts:
        print("Грамматика не LL(1):", file=sys.stderr)
        for c in g.conflicts:
            print("  " + c, file=sys.stderr)
    if table_only:
        status = "конфликтов нет, грамматика LL(1)" if not g.conflicts else "есть конфликты"
        stdout.append(f"Таблица предиктивного анализа: {table_file} ({status})\n")
        flush()
        return 0 if not g.conflicts else 1

    try:
        with open(input_path, "rb") as f:
            source = f.read()
    except OSError:
        print(f"не удалось открыть файл {input_path}", file=sys.stderr)
        return 2

    # 2. Лексический анализ.
    lex_errors: list[Diagnostic] = []
    tokens = Lexer(source).tokenize(lex_errors)

    # 3. Синтаксический анализ с восстановлением.
    parser = Parser(g, tokens, phrase)
    parser.run()

    # 4. Сводим ошибки в один список по порядку в тексте (sorted устойчив, как stable_sort).
    all_errors = sorted(lex_errors + parser.errors, key=lambda d: (d.line, d.col))

    # Строки исходника, как при построчном чтении: последний '\n' не даёт пустой строки, '\r' в конце срезаем.
    lines = source.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    lines = [l[:-1] if l.endswith(b"\r") else l for l in lines]

    mode_name = "режим фразы" if phrase else "режим паники"
    grammar_name = "расширенная (--ext)" if ext else "из методички"
    stdout.append(f"Файл: {input_path}\nГрамматика: {grammar_name}, восстановление: {mode_name}\n\n")
    for d in all_errors:  # ЦИКЛ по найденным ошибкам
        stdout.append(f"{input_path}:{d.line}:{d.col}: {d.category} ошибка [{d.type}]: {d.message}\n")
        stdout.append(source_line(lines, d.line, d.col))
        if d.skipped:
            stdout.append("  при восстановлении пропущено:" + "".join(f" '{s}'" for s in d.skipped) + "\n")
    if parser.aborted:
        stdout.append("Внимание: разбор прерван защитой от зацикливания\n")
    if not all_errors:
        stdout.append("Программа корректна.\n")
    stdout.append(("\n" if all_errors else "") + f"Итого ошибок: {len(all_errors)} (лексических: {len(lex_errors)}"
                  f", синтаксических: {len(parser.errors)})\n")

    # 5. Таблица хода разбора, как в примере 4 методички.
    name = os.path.basename(input_path)
    stem = os.path.splitext(name)[0]
    trace_file = os.path.join(out_dir, stem + (".phrase.trace.md" if phrase else ".trace.md"))
    src = text_of(source)
    if src and not src.endswith("\n"):
        src += "\n"  # закрывающие ``` должны стоять с новой строки
    out = [f"# Ход разбора: {name}\n\nГрамматика: {grammar_name}, восстановление: {mode_name}.\n\n"
           f"## Исходный текст\n\n```c\n{src}```\n\n"
           f"## Ошибки ({len(all_errors)})\n\n"]
    if not all_errors:
        out.append("Ошибок нет.\n")
    # Лексические — списком, синтаксические — под теми же номерами, что «Ошибка N» в таблице.
    for d in lex_errors:
        out.append(f"- {d.line}:{d.col} — лексическая [{d.type}]: {d.message}\n")
    if lex_errors and parser.errors:
        out.append("\n")
    for i, d in enumerate(parser.errors, 1):
        out.append(f"{i}. {d.line}:{d.col} — синтаксическая [{d.type}]: {d.message}\n")
    out.append("\n## Таблица разбора\n\nСтек: дно `$` слева, вершина справа. Вход: текущий токен первый, "
               "длинный хвост сокращён до 10 токенов.\n\n")
    rows = [[str(i), f"`{r.stack}`", f"`{r.input}`", r.note] for i, r in enumerate(parser.trace, 1)]
    write_table(out, ["№", "Стек", "Вход", "Примечание"], rows)
    with open(trace_file, "wb") as f:
        f.write(to_bytes("".join(out)))

    stdout.append(f"Таблица хода разбора: {trace_file}\nТаблица предиктивного анализа: {table_file}\n")
    flush()
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
