# ЛР2 ТАЯК. Конечный автомат: чтение из файла, анализ, детерминизация,
# разбор строк. Здесь — аргументы командной строки и порядок вывода.
# Запуск: python3 main.py <файл автомата> [строка ...] [--dot] [--dfa-out файл]
import signal
import sys

from automaton import (START, FiniteAutomaton, RuleFileReader, show_set,
                       show_sym)

out = sys.stdout


def usage() -> None:
    out.write("Использование: python3 main.py <файл автомата> [строка ...] [--dot] [--dfa-out <файл>]\n"
              "  строки после имени файла проверяются сразу; если их нет —\n"
              "  вводятся с клавиатуры по одной, пустая строка или Ctrl+D — выход.\n"
              "  --dot              записать графы <файл>.dot и <файл>.dfa.dot (Graphviz)\n"
              "  --dfa-out <файл>   сохранить правила ДКА в формате входного файла\n")


def join_states(states) -> str:
    return " ".join(s.name() for s in states) or "нет"


def describe(fa: FiniteAutomaton) -> None:
    """Общие сведения: состояния, алфавит, таблица переходов."""
    st, fin, alpha = fa.states(), fa.finals(), fa.alphabet()
    out.write(f"Состояний: {len(st)}: {join_states(st)}\n"
              "Начальное: q0\n"
              f"Конечных: {len(fin)}: {join_states(fin)}\n"
              f"Алфавит ({len(alpha)}):")
    for s in alpha:
        out.write(" " + show_sym(s))
    out.write(f"\nПравил: {len(fa.rules())}\n\n")

    if len(alpha) <= 24:
        out.write("Таблица переходов (-> начальное, * конечное, - перехода нет):\n")
        fa.print_table(out)
    else:
        out.write(f"Таблица переходов не выводится: в алфавите {len(alpha)} символов.\n")


def report_hanging(fa: FiniteAutomaton) -> None:
    """Висячие вершины: недостижимые из q0 и тупиковые (конечное недостижимо)."""
    unreach, dead = fa.unreachable(), fa.dead()

    if not unreach:
        out.write("Недостижимых состояний нет: в каждое можно попасть из q0.\n")
    else:
        out.write(f"Недостижимые из q0 состояния: {join_states(unreach)} — их правила никогда не сработают.\n")

    if not dead:
        out.write("Тупиковых состояний нет: из каждого можно дойти до конечного.\n")
        return
    out.write("Тупиковые состояния (из них не дойти ни до одного конечного):\n")
    for s in dead:
        what = ("переходы есть, но все ведут в тупик или по кругу" if fa.has_outgoing(s)
                else "из него нет ни одного перехода")
        also = " (к тому же недостижимо)" if s in unreach else ""
        out.write(f"  {s.name()} — {what}{also}\n")
    if START in dead:
        out.write("  Тупик — само q0, поэтому автомат не допускает ни одной строки.\n")


def check_string(text: str, dfa: FiniteAutomaton, original: FiniteAutomaton, was_nfa: bool) -> None:
    """Проверка одной строки и вывод заключения."""
    r = dfa.run(text)
    out.write(f'"{text}" — ' + ("ДОПУСКАЕТСЯ" if r.accepted else "НЕ ДОПУСКАЕТСЯ"))
    if not r.accepted:
        out.write(": " + r.reason)
    out.write("\n")

    # Путь по автомату: q0 -'a'-> q2 -'b'-> q3 ...
    path = r.path[0].name()
    for i in range(1, len(r.path)):
        path += f" -{show_sym(r.input[i - 1])}-> {r.path[i].name()}"
    out.write("    путь" + (" по ДКА" if was_nfa else "") + ": " + path + "\n")

    if was_nfa:  # сверка: прямое моделирование НКА должно дать тот же ответ
        if original.run_nfa(text) == r.accepted:
            out.write("    (моделирование исходного НКА даёт тот же ответ)\n")
        else:
            out.write("    ВНИМАНИЕ: НКА и ДКА разошлись — ошибка в детерминизации!\n")


def open_out(path: str):
    """Файл для записи: байты, не ставшие UTF-8, вернутся как были."""
    return open(path, "w", encoding="utf-8", errors="surrogateescape", newline="")


def main(argv: list[str]) -> int:
    # ---- разбор аргументов ----
    file, dfa_out = "", ""
    strings: list[str] = []
    dot = have_strings = False
    i = 0
    while i < len(argv):  # ЦИКЛ: по аргументам командной строки
        a = argv[i]
        if a in ("-h", "--help"):
            usage()
            return 0
        if a == "--dot":
            dot = True
        elif a == "--dfa-out":
            if i + 1 == len(argv):
                sys.stderr.write("Ошибка: после --dfa-out нужно имя файла\n")
                return 2
            i += 1
            dfa_out = argv[i]
        elif not file:
            file = a
        else:
            strings.append(a)
            have_strings = True
        i += 1
    if not file:
        usage()
        return 2

    # ---- чтение файла ----
    out.write(f"=== Файл {file} ===\n")
    try:
        reader = RuleFileReader(file)
    except RuntimeError as e:
        out.flush()
        sys.stderr.write(f"Ошибка: {e}\n")
        return 1
    out.write(f"Строк в файле: {reader.total_lines()}, правил: {len(reader.rules())}, "
              f"пустых и комментариев: {reader.skipped_lines()}, с ошибками: {len(reader.errors())}\n")

    if reader.errors():
        out.write("\n=== Синтаксические ошибки (эти строки пропущены) ===\n")
        for e in reader.errors():
            out.write(f'  строка {e.line}: "{e.text}" — {e.message}\n')
    if not reader.rules():
        out.write("\nВ файле нет ни одного правильного правила — строить нечего.\n")
        return 1

    fa = FiniteAutomaton(reader.rules())
    if fa.duplicates():
        out.write("\n=== Повторяющиеся правила (учтены один раз) ===\n")
    for d in fa.duplicates():
        out.write(f"  строка {d.line}: правило {d.from_.name()},{d.sym}={d.to.name()} уже было выше\n")

    # ---- информация об автомате ----
    out.write("\n=== Автомат ===\n")
    describe(fa)
    if not fa.has_transitions_from_start():
        out.write("\nВнимание: из начального состояния q0 нет переходов.\n")
    if not fa.finals():
        out.write("\nВнимание: конечных состояний (f<N>) нет — ни одна строка не будет допущена.\n")

    out.write("\n=== Детерминированность ===\n")
    conf = fa.conflicts()
    nfa = bool(conf)
    if not nfa:
        out.write("Автомат ДЕТЕРМИНИРОВАН: из каждого состояния по каждому символу не больше одного перехода.\n")
    else:
        out.write("Автомат НЕДЕТЕРМИНИРОВАН: по одному символу из одного состояния есть переходы\n"
                  f"в разные состояния ({len(conf)} случ.):\n")
        for c in conf:  # ЦИКЛ: по конфликтующим парам (состояние, символ)
            to = {r.to for r in c.rules}
            lines = ", ".join(str(r.line) for r in c.rules)
            out.write(f"  {c.from_.name()} по {show_sym(c.sym)} -> {show_set(to)}   (строки {lines})\n")

    out.write("\n=== Висячие вершины ===\n")
    report_hanging(fa)

    # ---- детерминизация ----
    det = fa.determinize()
    if nfa:
        out.write("\n=== Детерминизация (построение подмножеств) ===\n"
                  "Состояния ДКА (в порядке появления) и из чего они состоят:\n")
        for st, states in det.composition:
            note = ""
            if len(states) > 1 and st.final:
                note = "   конечное: содержит конечное состояние"
            elif len(states) > 1:
                note = "   новое"
            out.write(f"  {st.name()} = {show_set(states)}{note}\n")
        out.write("\nПереходы ДКА в формате входного файла:\n")
        det.dfa.print_rules(out)
        out.write("\n")
        describe(det.dfa)
        dead_dfa = det.dfa.dead()
        if dead_dfa:
            out.write(f"Тупиковые состояния ДКА: {join_states(dead_dfa)}\n")

    # ---- выгрузка в файлы ----
    if dfa_out:
        try:
            with open_out(dfa_out) as f:
                (det.dfa if nfa else fa).print_rules(f)
            out.write(f"\nПравила {'ДКА' if nfa else 'автомата'} сохранены в {dfa_out}\n")
        except OSError:
            out.flush()
            sys.stderr.write(f"Ошибка: не удалось записать {dfa_out}\n")
    if dot:
        title = file[file.rfind("/") + 1:]  # имя без каталога
        # Расширение срезаем только у имени файла: точки в "../" или "./" не трогаем.
        base = file
        dot_pos = title.rfind(".")
        if dot_pos > 0:
            base = file[:len(file) - (len(title) - dot_pos)]
        try:  # ошибка записи графа не останавливает программу
            with open_out(base + ".dot") as f:
                fa.write_dot(f, title + (" (НКА)" if nfa else ""))
        except OSError:
            pass
        out.write(f"\nГраф записан в {base}.dot")
        if nfa:
            try:
                with open_out(base + ".dfa.dot") as f:
                    det.dfa.write_dot(f, title + " (ДКА)", dict(det.composition))
            except OSError:
                pass
            out.write(f" и {base}.dfa.dot")
        out.write(f"\nКартинка: nix shell nixpkgs#graphviz -c dot -Tpng {base}"
                  ".dot -o graph.png  (или вставить текст на graphviz.online)\n")

    # ---- разбор строк ----
    worker = det.dfa if nfa else fa
    out.write("\n=== Проверка строк" + (" (через ДКА)" if nfa else "") + " ===\n")
    if have_strings:
        for s in strings:
            check_string(s, worker, fa, nfa)
        return 0

    tty = sys.stdin.isatty()
    if tty:
        out.write("Вводите строки по одной; пустая строка или Ctrl+D — выход.\n")
    while True:  # ЦИКЛ: пока пользователь вводит строки
        if tty:
            out.write("> ")
            out.flush()
        raw_line = sys.stdin.buffer.readline()
        if not raw_line:  # Ctrl+D
            break
        line = raw_line.removesuffix(b"\n").removesuffix(b"\r").decode("utf-8", "surrogateescape")
        if not line:
            break
        check_string(line, worker, fa, nfa)
    return 0


if __name__ == "__main__":
    # Ctrl+C и "| head" завершают программу молча, а не
    # трассировкой KeyboardInterrupt / BrokenPipeError.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    # Вывод в UTF-8; байты cp1251 из файла и аргументов выводятся как были.
    sys.stdout.reconfigure(encoding="utf-8", errors="surrogateescape", newline="\n")
    sys.stderr.reconfigure(encoding="utf-8", errors="surrogateescape")
    sys.exit(main(sys.argv[1:]))
