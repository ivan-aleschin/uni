# ЛР2 ТАЯК: конечный автомат, чтение из файла, анализ и детерминизация.
# Классы: State, Rule, RuleFileReader (чтение файла), FiniteAutomaton (анализ).
#
# Про строки. Python работает со str, а файл может быть не в UTF-8. Чтобы ничего
# не терялось, файл и аргументы декодируются как UTF-8 с errors="surrogateescape":
# байты, которые не складываются в UTF-8 (cp1251), превращаются в «заменители»
# и при выводе возвращаются ровно теми же байтами. Деление на символы и
# сортировка символов делаются по исходным байтам (функция raw).
from collections import deque
from dataclasses import dataclass, field
from typing import NamedTuple

SPACES = " \t\n\v\f\r"  # только ASCII-пробелы: str.strip() срезал бы и неразрывный
DIGITS = "0123456789"   # str.isdigit() принял бы и арабские цифры, поэтому явно


class State(NamedTuple):
    """Состояние: q<N> — обычное, f<N> — конечное. q0 и f0 — разные состояния.
    Кортеж (конечное?, номер) сортируется так: сначала все q, потом все f."""
    final: bool
    num: int

    def name(self) -> str:
        return ("f" if self.final else "q") + str(self.num)


START = State(False, 0)  # начальное состояние всегда q0


@dataclass
class Rule:
    """Одно правило q<N>,<C>=<q|f><N> и номер строки файла (0 — построено программой)."""
    from_: State
    sym: str
    to: State
    line: int = 0


@dataclass
class SyntaxError_:
    """Синтаксическая ошибка: номер строки, сама строка и что не так.
    Подчёркивание — чтобы не перекрыть встроенный SyntaxError."""
    line: int
    text: str
    message: str


@dataclass
class Conflict:
    """Из одного состояния по одному символу есть правила в разные состояния."""
    from_: State
    sym: str
    rules: list[Rule]


@dataclass
class RunResult:
    """Результат разбора строки детерминированным автоматом."""
    accepted: bool = False
    path: list[State] = field(default_factory=list)  # пройденные состояния, начиная с q0
    input: list[str] = field(default_factory=list)   # строка, разбитая на символы
    reason: str = ""                                  # почему отвергнута


# ---------- символы ----------

def raw(s: str) -> bytes:
    """Исходные байты строки — по ним режем на символы и сортируем."""
    return s.encode("utf-8", "surrogateescape")


def sym_len(b: bytes, i: int) -> int:
    """Сколько байт занимает символ с позиции i. Правильный UTF-8 — один символ;
    если байты не складываются в UTF-8 (cp1251), каждый байт — отдельный символ."""
    c = b[i]
    if c < 0x80:
        n = 1
    elif c & 0xE0 == 0xC0:
        n = 2
    elif c & 0xF0 == 0xE0:
        n = 3
    elif c & 0xF8 == 0xF0:
        n = 4
    else:
        n = 1
    if i + n > len(b):
        return 1
    for k in range(1, n):
        if b[i + k] & 0xC0 != 0x80:  # не байт-продолжение
            return 1
    return n


def split_symbols(s: str) -> list[str]:
    """Строка -> список символов (символ UTF-8 или одиночный байт)."""
    b = raw(s)
    out = []
    i = 0
    while i < len(b):
        n = sym_len(b, i)
        out.append(b[i:i + n].decode("utf-8", "surrogateescape"))
        i += n
    return out


def display_width(s: str) -> int:
    """Ширина на экране: символы, а не байты (для таблицы)."""
    return len(split_symbols(s))


def show_sym(s: str) -> str:
    """Символ в кавычках: 'a', ' ', '\\t', управляющие — как '\\x01'."""
    if s == "\t":
        return "'\\t'"
    if len(s) == 1 and ord(s) < 0x20:
        return f"'\\x{ord(s):02X}'"
    return "'" + s + "'"


def show_set(states) -> str:
    """{q1, q3, f0} — состояния по порядку."""
    return "{" + ", ".join(s.name() for s in sorted(states)) + "}"


# ---------- чтение файла ----------

def read_number(s: str, pos: int):
    """Номер состояния с позиции pos: (номер, новая позиция) или None, если цифр
    нет или их больше 18 (с запасом: номер влезает в 64 бита)."""
    start = pos
    while pos < len(s) and s[pos] in DIGITS:
        pos += 1
    if pos == start or pos - start > 18:
        return None
    return int(s[start:pos]), pos


def read_state_letter(c: str):
    """Буква состояния: q — обычное (False), f — конечное (True), иначе None."""
    if c in ("q", "Q"):
        return False
    if c in ("f", "F"):
        return True
    return None


def quote_char(s: str, pos: int) -> str:
    return show_sym(split_symbols(s[pos:])[0]) if pos < len(s) else "конец строки"


class RuleFileReader:
    """Чтение файла с правилами. Ошибочные строки не останавливают чтение:
    они попадают в errors(), а правильные — в rules()."""

    def __init__(self, path: str):
        try:
            with open(path, "rb") as f:
                data = f.read()
        except IsADirectoryError:
            data = b""  # ifstream открывает каталог, но не читает ни строки
        except OSError:
            raise RuntimeError("не удалось открыть файл " + path)

        self._rules: list[Rule] = []
        self._errors: list[SyntaxError_] = []
        self._total_lines = 0
        self._skipped_lines = 0

        lines = data.split(b"\n")  # getline делит только по '\n'
        if lines[-1] == b"":
            lines.pop()            # после последнего '\n' строки нет
        for raw_line in lines:
            self._total_lines += 1
            # Блокнот Windows может записать в начало файла метку UTF-8 (BOM).
            if self._total_lines == 1 and raw_line.startswith(b"\xef\xbb\xbf"):
                raw_line = raw_line[3:]
            # '\r' от Windows и пробелы по краям срезаем; пробел-символ стоит
            # в середине правила ("q3, =q3"), его это не задевает.
            line = raw_line.decode("utf-8", "surrogateescape").strip(SPACES)

            # Пустые строки и комментарии (';' или '#') пропускаем.
            if not line or line[0] in ";#":
                self._skipped_lines += 1
                continue

            rule, err = self.parse_line(line)
            if rule is not None:
                rule.line = self._total_lines
                self._rules.append(rule)
            else:
                self._errors.append(SyntaxError_(self._total_lines, line, err))

    def rules(self) -> list[Rule]:
        return self._rules

    def errors(self) -> list[SyntaxError_]:
        return self._errors

    def total_lines(self) -> int:
        return self._total_lines

    def skipped_lines(self) -> int:
        return self._skipped_lines

    @staticmethod
    def parse_line(line: str):
        """Разбор одной строки: (правило, "") или (None, текст ошибки)."""
        pos = 0

        # 1. Исходное состояние: q<N> (f<N> тоже можно — так записывается ДКА)
        from_final = read_state_letter(line[pos])
        if from_final is None:
            return None, "строка должна начинаться с 'q' (или 'f'), а начинается с " + quote_char(line, pos)
        pos += 1
        got = read_number(line, pos)
        if got is None:
            return None, "после '" + line[0] + "' нет номера состояния (или он длиннее 18 цифр)"
        from_num, pos = got

        # 2. Запятая
        if pos >= len(line) or line[pos] != ",":
            return None, "после номера состояния ожидалась ',', а стоит " + quote_char(line, pos)
        pos += 1

        # 3. Ровно один символ — любой, включая пробел, ',', '=' и ';'
        if pos >= len(line):
            return None, "после ',' нет символа перехода"
        sym = split_symbols(line[pos:])[0]
        pos += len(sym)

        # 4. Знак '='
        if pos >= len(line) or line[pos] != "=":
            # Частый случай: "q1,=q2" — забыли символ
            if sym == "=" and pos < len(line) and read_state_letter(line[pos]) is not None:
                return None, "после ',' сразу '=' — нет символа перехода (ε-переходы формат не допускает)"
            return None, ("после символа " + show_sym(sym) + " ожидался '=', а стоит " +
                          quote_char(line, pos) + " (символ перехода должен быть ровно один)")
        pos += 1

        # 5. Целевое состояние q<N> или f<N>
        to_final = read_state_letter(line[pos]) if pos < len(line) else None
        if to_final is None:
            return None, "после '=' ожидалось состояние q<N> или f<N>, а стоит " + quote_char(line, pos)
        letter = line[pos]  # q или f — для сообщения об ошибке
        pos += 1
        got = read_number(line, pos)
        if got is None:
            return None, "после '" + letter + "' нет номера состояния (или он длиннее 18 цифр)"
        to_num, pos = got

        # 6. После номера ничего быть не должно
        if pos != len(line):
            return None, "лишние символы после номера состояния: '" + line[pos:] + "'"
        return Rule(State(from_final, from_num), sym, State(to_final, to_num)), ""


# ---------- автомат ----------

class FiniteAutomaton:
    """Конечный автомат (в общем случае недетерминированный).
    Функция переходов: delta[состояние][символ] = множество состояний."""

    def __init__(self, rules: list[Rule] = ()):
        self._rules: list[Rule] = []       # уникальные правила в порядке добавления
        self._duplicates: list[Rule] = []  # отброшенные повторы
        self._delta: dict[State, dict[str, set[State]]] = {}
        self._all_states: set[State] = set()
        for r in rules:
            self.add_rule(r)

    def add_rule(self, r: Rule) -> bool:
        """Добавить правило. False — точно такое же правило уже было."""
        to = self._delta.setdefault(r.from_, {}).setdefault(r.sym, set())
        if r.to in to:  # РАЗВИЛКА: дубликат
            self._duplicates.append(r)
            return False
        to.add(r.to)
        self._rules.append(r)
        self._all_states.add(r.from_)
        self._all_states.add(r.to)
        return True

    def rules(self) -> list[Rule]:
        return self._rules

    def duplicates(self) -> list[Rule]:
        return self._duplicates

    def states(self) -> list[State]:
        return sorted(self._all_states | {START})  # q0 есть всегда

    def finals(self) -> list[State]:
        return sorted(s for s in self._all_states if s.final)

    def alphabet(self) -> list[str]:
        return sorted({r.sym for r in self._rules}, key=raw)

    def has_transitions_from_start(self) -> bool:
        return START in self._delta

    def has_outgoing(self, s: State) -> bool:
        return s in self._delta

    def targets(self, state: State, sym: str) -> set[State]:
        """Куда можно перейти из state по sym (пусто — перехода нет)."""
        return self._delta.get(state, {}).get(sym, set())

    def expected_symbols(self, state: State) -> list[str]:
        """Символы, по которым из state есть переходы (по порядку байтов)."""
        return sorted(self._delta.get(state, {}), key=raw)

    # ----- анализ -----

    def conflicts(self) -> list[Conflict]:
        """Пусто <=> автомат детерминирован. Группы правил с одной парой
        (состояние, символ); дубликаты уже отброшены, значит, цели разные."""
        groups: dict[tuple[State, str], list[Rule]] = {}
        for r in self._rules:
            groups.setdefault((r.from_, r.sym), []).append(r)
        out = []
        for (st, sym), rules in sorted(groups.items(), key=lambda kv: (kv[0][0], raw(kv[0][1]))):
            if len(rules) > 1:
                out.append(Conflict(st, sym, rules))
        return out

    def is_deterministic(self) -> bool:
        return not self.conflicts()

    def unreachable(self) -> list[State]:
        """Недостижимые из q0: обход в ширину по стрелкам."""
        seen = {START}
        q = deque([START])
        while q:  # ЦИКЛ: пока есть необработанные состояния
            cur = q.popleft()
            for to in self._delta.get(cur, {}).values():
                for t in to:
                    if t not in seen:
                        seen.add(t)
                        q.append(t)
        return [s for s in self.states() if s not in seen]

    def dead(self) -> list[State]:
        """Тупиковые: обход в ширину от конечных против стрелок,
        кого не посетили — из того конечное недостижимо."""
        reverse: dict[State, set[State]] = {}
        for r in self._rules:
            reverse.setdefault(r.to, set()).add(r.from_)
        seen = set(self.finals())
        q = deque(seen)
        while q:  # ЦИКЛ: обход назад от конечных
            cur = q.popleft()
            for prev in reverse.get(cur, ()):
                if prev not in seen:
                    seen.add(prev)
                    q.append(prev)
        return [s for s in self.states() if s not in seen]

    # ----- детерминизация -----

    def determinize(self) -> "Determinized":
        """Построение подмножеств. Составные состояния получают номера после
        самых больших старых; одиночное {qK} сохраняет имя qK."""
        res = Determinized(FiniteAutomaton(), [])
        next_q = next_f = 0
        for s in self.states():
            if s.final:
                next_f = max(next_f, s.num + 1)
            else:
                next_q = max(next_q, s.num + 1)

        names: dict[frozenset[State], State] = {}  # множество старых -> новое состояние
        todo: deque[frozenset[State]] = deque()

        def name_of(states: frozenset[State]) -> State:
            """Имя для множества; новое множество сразу ставим в очередь."""
            nonlocal next_q, next_f
            if states in names:
                return names[states]
            if len(states) == 1:
                n = next(iter(states))
            elif any(s.final for s in states):  # конечное, если есть хоть одно конечное
                n = State(True, next_f)
                next_f += 1
            else:
                n = State(False, next_q)
                next_q += 1
            names[states] = n
            res.composition.append((n, states))
            todo.append(states)
            return n

        name_of(frozenset({START}))
        while todo:  # ЦИКЛ: пока есть необработанные множества
            cur = todo.popleft()
            # t(q', a) = объединение t(q, a) по всем q из q'
            moves: dict[str, set[State]] = {}
            for s in cur:
                for sym, to in self._delta.get(s, {}).items():
                    moves.setdefault(sym, set()).update(to)
            frm = names[cur]
            for sym in sorted(moves, key=raw):
                res.dfa.add_rule(Rule(frm, sym, name_of(frozenset(moves[sym])), 0))
        return res

    # ----- разбор строки -----

    def _expected(self, s: State) -> str:
        return ", ".join(show_sym(sym) for sym in self.expected_symbols(s))

    def run(self, text: str) -> RunResult:
        """Разбор строки детерминированным автоматом: путь и причина отказа."""
        res = RunResult()
        res.input = split_symbols(text)
        cur = START
        res.path.append(cur)

        for i, sym in enumerate(res.input):  # ЦИКЛ: по символам строки
            nxt = self.targets(cur, sym)
            if len(nxt) > 1:
                raise RuntimeError("run() вызван для недетерминированного автомата")
            if not nxt:  # РАЗВИЛКА: перехода нет — строка отвергнута
                why = f"символ №{i + 1} {show_sym(sym)}: "
                if not self.has_outgoing(cur):
                    why += f"из {cur.name()} переходов нет вообще, строка должна была здесь закончиться"
                else:
                    why += f"из {cur.name()} по нему перехода нет, ожидалось: {self._expected(cur)}"
                if sym not in self.alphabet():
                    why += f" (символа {show_sym(sym)} нет в алфавите)"
                res.reason = why
                return res
            cur = next(iter(nxt))
            res.path.append(cur)

        res.accepted = cur.final  # строка кончилась: допуск, если стоим в конечном
        if not res.accepted:
            if not res.input:
                res.reason = "пустая строка: q0 не конечное состояние"
            else:
                res.reason = f"строка закончилась в состоянии {cur.name()}, оно не конечное"
                if self.has_outgoing(cur):
                    res.reason += "; дальше ожидалось: " + self._expected(cur)
        return res

    def run_nfa(self, text: str) -> bool:
        """Прямое моделирование НКА множеством текущих состояний."""
        cur = {START}
        for sym in split_symbols(text):  # ЦИКЛ: по символам строки
            nxt = set()
            for s in cur:
                nxt |= self.targets(s, sym)
            if not nxt:
                return False
            cur = nxt
        return any(s.final for s in cur)

    # ----- вывод -----

    def print_rules(self, out) -> None:
        """Правила в формате входного файла."""
        for r in self._rules:
            out.write(f"{r.from_.name()},{r.sym}={r.to.name()}\n")

    def print_table(self, out) -> None:
        """Таблица переходов: '-' — перехода нет, qK или {qA,qB} у НКА."""
        syms = self.alphabet()
        rows = self.states()

        def cell(s: State, sym: str) -> str:
            t = sorted(self.targets(s, sym))
            if not t:
                return "-"
            if len(t) == 1:
                return t[0].name()
            return "{" + ",".join(x.name() for x in t) + "}"

        def row_label(s: State) -> str:
            return ("->" if s == START else "  ") + ("*" if s.final else " ") + s.name()

        def pad(s: str, width: int) -> str:
            return s + " " * (width - min(width, display_width(s)))

        label_w = max(len(row_label(s)) for s in rows)
        w = []
        for sym in syms:
            w.append(max([display_width(show_sym(sym))] + [len(cell(s, sym)) for s in rows]))

        out.write(pad("", label_w))
        for j, sym in enumerate(syms):
            out.write(" | " + pad(show_sym(sym), w[j]))
        out.write("\n" + "-" * label_w)
        for j in range(len(syms)):
            out.write("-+-" + "-" * w[j])
        out.write("\n")
        for s in rows:  # ЦИКЛ: строка таблицы на каждое состояние
            row = pad(row_label(s), label_w)
            for j, sym in enumerate(syms):
                row += " | " + pad(cell(s, sym), w[j])
            out.write(row.rstrip(" ") + "\n")  # без хвостовых пробелов

    def write_dot(self, out, title: str, composition: dict | None = None) -> None:
        """Граф Graphviz: конечные — прямоугольники, недостижимые серые
        пунктирные, тупиковые красные; у составных состояний ДКА подписано множество."""
        composition = composition or {}
        unreach = set(self.unreachable())
        dead_set = set(self.dead())

        out.write(f'digraph "{dot_escape(title)}" {{\n'
                  "  rankdir=LR;\n"
                  f'  label="{dot_escape(title)}"; labelloc=t; fontname="Helvetica";\n'
                  '  node [shape=circle, fontname="Helvetica"];\n'
                  '  edge [fontname="Helvetica"];\n'
                  "  start [shape=point];\n"
                  "  start -> q0;\n")

        for s in self.states():
            label = s.name()
            if len(composition.get(s, ())) > 1:
                label += "\\n" + show_set(composition[s])
            line = f'  {s.name()} [label="{label}"'
            if s.final:
                line += ", shape=box"
            if s in unreach:
                line += ", style=dashed, color=gray, fontcolor=gray"
            elif s in dead_set:
                line += ", color=red, fontcolor=red"
            out.write(line + "];\n")

        # Все символы между одной парой состояний — одной стрелкой.
        edges: dict[tuple[State, State], str] = {}
        for r in self._rules:
            lbl = edges.get((r.from_, r.to), "")
            edges[(r.from_, r.to)] = lbl + (" " if lbl else "") + show_sym(r.sym)
        for (a, b), lbl in sorted(edges.items()):
            out.write(f'  {a.name()} -> {b.name()} [label="{dot_escape(lbl)}"];\n')
        out.write("}\n")


def dot_escape(s: str) -> str:
    """Экранирование кавычек и обратной косой черты для DOT."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


@dataclass
class Determinized:
    """Результат детерминизации: ДКА и состав каждого его состояния
    (в порядке появления при обходе)."""
    dfa: FiniteAutomaton
    composition: list[tuple[State, frozenset[State]]]
