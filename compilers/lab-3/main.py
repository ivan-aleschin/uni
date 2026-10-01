# ЛР3 по ТАЯК: недетерминированный магазинный (МП) автомат, построенный по КС-грамматике.
#
# Только стандартная библиотека Python; запуск: python3 main.py <файл грамматики>.
# Программа читает грамматику из файла, строит по ней автомат так,
# как описано в методичке (одно состояние s0, команды (1)-(4)), печатает его описание, а потом
# для каждой введённой цепочки ищет последовательность тактов, приводящую в заключительную
# конфигурацию. Автомат недетерминированный, поэтому поиск идёт с возвратом (перебор в глубину).

import math
import re
import sys

# Маркер дна магазина h0. В файле грамматики управляющих символов быть не может,
# поэтому \x01 ни с одним терминалом не совпадёт.
H0 = "\x01"
# «Бесконечная» длина — для нетерминалов, из которых не выводится ни одна терминальная цепочка.
# inf + 1 = inf, так что отдельное «сложение с насыщением» не нужно.
INF = math.inf
# Предохранитель: больше стольких конфигураций за один разбор не просматриваем.
MAX_VISITED = 2_000_000


def is_nonterminal(c):
    return "A" <= c <= "Z"


# То же условие для поиска первого нетерминала в строке (нужно в tail_matches).
NONTERMINAL = re.compile("[A-Z]")


# Как символ показывается человеку: пробел — как ~ (так же он задаётся в файле), дно — как h0.
def show_char(c):
    if c == H0:
        return "h0"
    if c == " ":
        return "~"
    return c


# Цепочка символов для печати; пустая цепочка печатается как ε.
def show(s):
    if not s:
        return "ε"
    # То же, что show_char для каждого символа, но целиком: на длинных цепочках (тысячи
    # конфигураций по тысяче символов) посимвольный цикл заметно медленнее replace.
    return s.replace(" ", "~").replace(H0, "h0")


# Длина строки в «знаках» на экране. Ввод читается как UTF-8 с surrogateescape: каждый
# неправильный байт становится символом \udc80..\udcff. Одиночные байты продолжения
# (\udc80..\udcbf) не считаем: они продолжают предыдущий символ UTF-8.
def screen_width(s):
    if s.isascii():
        return len(s)
    return sum(1 for c in s if not "\udc80" <= c <= "\udcbf")


# «1 такт», «3 такта», «12 тактов».
def tacts(n):
    d10, d100 = n % 10, n % 100
    if d10 == 1 and d100 != 11:
        word = "такт"
    elif 2 <= d10 <= 4 and (d100 < 12 or d100 > 14):
        word = "такта"
    else:
        word = "тактов"
    return f"{n} {word}"


# ---------------------------------------------------------------------------------------------
# Грамматика и её чтение из файла
# ---------------------------------------------------------------------------------------------

class Grammar:
    def __init__(self):
        self.start = ""          # I — левая часть первого правила
        self.nonterminals = []   # VN в порядке появления левых частей
        self.terminals = []      # VT в порядке первого появления
        self.rules = {}          # A -> список правых частей ("" = ε)


class GrammarError(Exception):
    pass


def error_at(line_no, msg):
    return GrammarError(f"строка {line_no}: {msg}")


def read_grammar(path):
    # Читаем байты и раскладываем их по символам один к одному (latin-1):
    # всё, что не печатный ASCII, всё равно отвергается проверкой ниже.
    try:
        with open(path, "rb") as f:
            data = f.read().decode("latin-1")
    except IsADirectoryError:
        data = ""  # каталог открыть можно, но читать из него нечего
    except OSError:
        raise GrammarError(f"не удалось открыть файл «{path}»")

    g = Grammar()
    used_on_right = []  # нетерминалы из правых частей и номер строки
    for line_no, line in enumerate(data.split("\n"), start=1):
        # Пробелы, табуляции и \r (файлы преподавателя сохранены в Windows) незначащие.
        s = "".join(c for c in line if c not in " \t\r")
        if not s:
            continue  # пустые строки просто пропускаем

        if any(not 0x20 <= ord(c) < 0x7F for c in s):
            raise error_at(line_no, "допустимы только печатные ASCII-символы "
                                    "(пробел-терминал записывается как ~)")

        # Первый '>' отделяет левую часть от правой, остальные '>' — обычные терминалы.
        arrow = s.find(">")
        if arrow < 0:
            raise error_at(line_no, "нет символа '>', отделяющего левую часть правила от правой")
        left = s[:arrow]
        if len(left) != 1 or not is_nonterminal(left):
            raise error_at(line_no, f"левая часть «{left}» должна быть одной заглавной "
                                    "латинской буквой")
        a = left
        if not g.start:
            g.start = a
        if a not in g.rules:
            g.nonterminals.append(a)
            g.rules[a] = []

        # Правая часть делится по '|'; пустая альтернатива означает ε-правило A -> ε.
        for alt in s[arrow + 1:].split("|"):
            alt = alt.replace("~", " ")  # ~ в файле — это терминал «пробел»
            for c in alt:
                if is_nonterminal(c):
                    used_on_right.append((c, line_no))
                elif c not in g.terminals:
                    g.terminals.append(c)
            if alt not in g.rules[a]:
                g.rules[a].append(alt)

    if not g.start:
        raise GrammarError("в файле нет ни одного правила")
    for b, ln in used_on_right:
        if b not in g.rules:
            raise error_at(ln, f"нетерминал {b} встречается в правой части, но правил для него нет")
    return g


# ---------------------------------------------------------------------------------------------
# Магазинный автомат
# ---------------------------------------------------------------------------------------------

# Конфигурация (s0, остаток входа, магазин) и номер команды, которой в неё пришли.
# Состояние у автомата одно, поэтому храним только позицию во входе и магазин.
class Config:
    __slots__ = ("pos", "stack", "cmd", "next")

    def __init__(self, pos, stack, cmd):
        self.pos = pos
        self.stack = stack  # дно слева (H0), вершина — последний символ
        self.cmd = cmd
        self.next = 0       # сколько переходов из неё перебор уже испробовал


# Чем закончился шаг в новую конфигурацию .
CUT, ACCEPT, OPEN = 0, 1, 2


class PushdownAutomaton:
    def __init__(self, g):
        self.g = g
        # Нумерация команд как в примере методички: сначала по одной команде (1) на каждый
        # нетерминал (альтернативы — подпункты k.1, k.2, ...), затем команды (2) для терминалов,
        # последней — команда (3) для дна магазина.
        self.nt_cmd = {}  # номер команды типа (1) для нетерминала
        self.t_cmd = {}   # номер команды типа (2) для терминала
        n = 0
        for a in g.nonterminals:
            n += 1
            self.nt_cmd[a] = n
        for a in g.terminals:
            n += 1
            self.t_cmd[a] = n
        self.h0_cmd = n + 1  # номер команды типа (3)

        self.max_rhs = max(len(rhs) for alts in g.rules.values() for rhs in alts)
        self.has_space = " " in g.terminals
        self.min_len = {}  # минимальная длина терминальной цепочки из A
        self.first = {}    # FIRST(A): с каких терминалов начинается вывод
        self.compute_min_lengths()
        self.compute_first_sets()
        # «Вес» каждого символа магазина для отсечения по длине: у терминала 1, у дна 0.
        self.weight = {H0: 0, **{a: 1 for a in g.terminals}, **self.min_len}

    # minLen(A) — длина самой короткой терминальной цепочки, выводимой из A.
    # Считаем итерациями до неподвижной точки: minLen(A) = min по правилам A -> X1..Xk
    # суммы minLen(Xi), где у терминала длина 1. Для ε-правила сумма равна 0.
    def compute_min_lengths(self):
        g = self.g
        for a in g.nonterminals:
            self.min_len[a] = INF
        changed = True
        while changed:  # ЦИКЛ: пока хоть одно значение уменьшается
            changed = False
            for a in g.nonterminals:
                for rhs in g.rules[a]:
                    length = sum(self.min_len[x] if is_nonterminal(x) else 1 for x in rhs)
                    if length < self.min_len[a]:
                        self.min_len[a] = length
                        changed = True

    # FIRST(A) — терминалы, с которых может начинаться цепочка, выводимая из A. Тоже неподвижная
    # точка: для A -> X1 X2 ... добавляем FIRST(X1), а если X1 обнуляемый (minLen = 0), то
    # и FIRST(X2), и так далее.
    # Нужно только для сообщения «что ожидалось» при отказе, на сам разбор не влияет.
    def compute_first_sets(self):
        g = self.g
        for a in g.nonterminals:
            self.first[a] = set()
        changed = True
        while changed:
            changed = False
            for a in g.nonterminals:
                f = self.first[a]
                before = len(f)
                for rhs in g.rules[a]:
                    for x in rhs:
                        if not is_nonterminal(x):
                            f.add(x)
                            break
                        f |= self.first[x]
                        if self.min_len[x] != 0:
                            break
                if len(f) != before:
                    changed = True

    # Ветвь зашла в тупик на позиции best_pos — запоминаем, какой символ она была готова прочитать
    # следующим: FIRST от содержимого магазина сверху вниз (или конец цепочки, если всё обнуляемо).
    def note_dead_end(self, pos, stack):
        if pos != self.best_pos:
            return
        for x in reversed(stack):
            if x == H0:
                break
            if not is_nonterminal(x):
                self.expected.add(x)
                return
            self.expected |= self.first[x]
            if self.min_len[x] != 0:
                return
        self.expected_end = True

    # Сколько входных символов как минимум «съест» содержимое магазина.
    # Считаем по различным символам через str.count — быстрее, чем складывать посимвольно.
    def min_length(self, stack):
        weight = self.weight
        return sum(weight[x] * stack.count(x) for x in set(stack))

    # Терминалы, лежащие подряд у самого дна, автомат прочитает последними, и снять их можно
    # только командой (2). Значит, они обязаны совпасть с концом входной цепочки:
    # stack[1] — с последним символом входа, stack[2] — с предпоследним и т.д.
    # Сравнение делается срезами строк, а не посимвольным циклом: при S -> Sa | Sb
    # у дна копятся сотни терминалов, и цикл по ним был бы слишком медленным.
    def tail_matches(self, pos, stack):
        inp = self.input
        m = NONTERMINAL.search(stack, 1)  # первый нетерминал над дном
        tail = stack[1:m.start() if m else len(stack)]
        if len(tail) > len(inp) - pos:
            return False
        return inp.endswith(tail[::-1])

    # Каждый терминал из магазина когда-нибудь будет снят командой (2), то есть прочитан.
    # Поэтому любого терминала в магазине не может быть больше, чем его осталось во входе.
    # При левой рекурсии E -> E+T каждый виток кладёт в магазин '+', и рекурсия обрывается,
    # как только плюсов в магазине становится больше, чем во входе.
    # Каждый терминал считаем через str.count — встроенной операцией,
    # без цикла по всему остатку входа.
    def terminals_fit(self, pos, stack):
        inp = self.input
        for x in set(stack):
            if x == H0 or is_nonterminal(x):
                continue
            if stack.count(x) > inp.count(x, pos):
                return False
        return True

    def rule_label(self, a, alt):
        label = f"({self.nt_cmd[a]}"
        if len(self.g.rules[a]) > 1:
            label += f".{alt + 1}"
        return label + ")"

    def print_definition(self, out):
        g = self.g

        def lst(items):
            return "{" + ", ".join(items) + "}"

        vn = [show_char(a) for a in g.nonterminals]
        vt = [show_char(a) for a in g.terminals]

        out.write("Грамматика G = {VN, VT, I, P}:\n")
        out.write(f"  VN = {lst(vn)}\n  VT = {lst(vt)}\n  I  = {g.start}\n")
        out.write("  Правила:\n")
        for a in g.nonterminals:
            out.write(f"    {a} -> " + " | ".join(show(alt) for alt in g.rules[a]) + "\n")

        z = vn + vt + ["h0"]
        out.write("\nМагазинный автомат M = {S, P, Z, δ, s0, h0, F}:\n")
        out.write(f"  S = {{s0}}\n  P = {lst(vt)}\n  Z = {lst(z)}\n")
        out.write("  s0 — начальное состояние, h0 — маркер дна магазина\n  F = {s0}\n")

        out.write("\nКоманды типа (1) — замена нетерминала в вершине правой частью правила (в реверсе):\n")
        for a in g.nonterminals:
            alts = g.rules[a]
            text = "; ".join(f"(s0, {show(alt[::-1])})" for alt in alts)
            if len(alts) > 1:
                text = "{" + text + "}"
            out.write(f"  ({self.nt_cmd[a]}) δ0(s0, ε, {a}) = {text}\n")
        out.write("Команды типа (2) — совпадение терминала на входе и в вершине:\n")
        for a in g.terminals:
            out.write(f"  ({self.t_cmd[a]}) δ(s0, {show_char(a)}, {show_char(a)}) = (s0, ε)\n")
        out.write("Команда типа (3) — переход в заключительную конфигурацию:\n")
        out.write(f"  ({self.h0_cmd}) δ(s0, ε, h0) = (s0, ε)\n")
        out.write(f"Тип (4) — начальная конфигурация: (s0, α, h0{g.start}), α — исходная цепочка\n")

        out.write("\nМинимальная длина выводимой цепочки (для отсечения перебора):")
        for a in g.nonterminals:
            m = self.min_len[a]
            out.write(f"  {a}: " + ("∞" if m == INF else str(m)))
        out.write("\n")
        for a in g.nonterminals:
            if self.min_len[a] == INF:
                out.write(f"Предупреждение: из {a} не выводится ни одна терминальная цепочка.\n")

    def config_text(self, c):
        return f"(s0, {show(self.input[c.pos:])}, {show(c.stack)})"

    def print_path(self, path, out):
        # Ширина колонки с номерами команд — по самой длинной конфигурации на пути.
        width = max(screen_width(self.config_text(c)) for c in path)
        for i, c in enumerate(path):
            text = self.config_text(c)
            line = ("├ " if i else "  ") + text
            if c.cmd:
                line += " " * (width - screen_width(text) + 3) + c.cmd
            out.write(line + "\n")

    # Левый вывод восстанавливается по успешной ветви: после каждой команды (1) сентенциальная
    # форма = уже прочитанная часть входа + содержимое магазина сверху вниз (без h0).
    def print_left_derivation(self, out):
        line = self.g.start
        path = self.path
        for i in range(1, len(path)):
            prev = path[i - 1]
            if not prev.stack or not is_nonterminal(prev.stack[-1]):
                continue
            c = path[i]
            form = self.input[:c.pos] + c.stack[::-1].replace(H0, "")
            line += " ⇒ " + show(form)
        out.write(f"Левый вывод: {line}\n")

    # Возврат: снимаем последнюю конфигурацию с ветви. Совпадать с best_path теперь может
    # только то, что на ветви осталось.
    def leave(self):
        self.path.pop()
        self.best_same = min(self.best_same, len(self.path))

    # Шаг в конфигурацию (s0, input[pos:], stack). Если она отсечена или из неё нет ни одного
    # перехода — CUT, если она заключительная — ACCEPT, иначе она остаётся на ветви (OPEN).
    def enter(self, pos, stack, cmd):
        visited = self.visited
        if len(visited) >= MAX_VISITED:
            self.aborted = True
            return CUT
        # Отсечение 1: в этой конфигурации уже были — всё, что из неё достижимо, уже проверено
        # (или проверяется прямо сейчас выше по ветви, и тогда это цикл).
        key = (pos, stack)
        if key in visited:
            self.cut_repeat += 1
            return CUT
        visited.add(key)

        path = self.path
        path.append(Config(pos, stack, cmd))
        st = stack
        if pos > self.best_pos or not self.best_path:  # РАЗВИЛКА: новый рекорд по прочитанному
            self.best_pos = pos
            # Дописываем только то, чем ветвь отличается от прошлой лучшей: копировать весь путь
            # на каждом прочитанном символе длинной цепочки слишком дорого.
            del self.best_path[self.best_same:]
            self.best_path.extend(path[self.best_same:])
            self.best_same = len(path)
            self.expected.clear()
            self.expected_end = False

        inp = self.input
        rest = len(inp) - pos
        is_open = False
        if self.min_length(st) > rest:
            # Отсечение 2: магазин заведомо породит больше символов, чем осталось на входе.
            # Именно оно обрывает левую рекурсию E -> E+T: каждый виток добавляет +T.
            self.cut_length += 1
        elif not self.terminals_fit(pos, st):
            # Отсечение 3: какого-то терминала в магазине больше, чем осталось во входе.
            self.cut_count += 1
        elif not self.tail_matches(pos, st):
            # Отсечение 4: терминалы у дна не совпадают с концом входа. Без него левая рекурсия
            # S -> Sa | Sb перебирает все 2^n вариантов «хвоста» до того, как прочитать хоть символ.
            self.cut_tail += 1
        elif len(st) > self.stack_limit:
            # Отсечение 5: нужно только для грамматик с ε-правилами (см. README).
            self.cut_stack += 1
        elif not st:
            # Дно уже снято командой (3): допускаем, только если вход прочитан полностью.
            if rest == 0:
                return ACCEPT
        elif is_nonterminal(st[-1]) or st[-1] == H0:
            is_open = True  # применима команда (1) или (3)
        else:
            is_open = rest > 0 and inp[pos] == st[-1]  # применима ли команда (2)
        if is_open:
            return OPEN
        self.note_dead_end(pos, st)  # для диагностики: что эта ветвь ждала дальше
        self.leave()
        return CUT

    # Перебор в глубину с возвратом. Рекурсии нет: ветвь лежит в self.path, и у каждой
    # конфигурации в поле next записано, сколько переходов из неё уже испробовано, — так цепочка
    # в тысячи символов не упирается в предел глубины рекурсии. Возвращает True, если дошли
    # до (s0, ε, ε); тогда self.path — вся успешная цепочка конфигураций.
    def search(self, initial):
        if self.enter(0, initial, "") == ACCEPT:
            return True
        path = self.path
        rules = self.g.rules
        while path and not self.aborted:  # ЦИКЛ: пока на ветви есть что продолжать
            c = path[-1]
            top = c.stack[-1]
            below = c.stack[:-1]
            pos, i = c.pos, c.next
            c.next += 1
            if is_nonterminal(top):  # РАЗВИЛКА: команда (1), альтернативы по порядку
                alts = rules[top]
                if i == len(alts):  # все альтернативы испробованы — возврат
                    self.leave()
                    continue
                e = self.enter(pos, below + alts[i][::-1], self.rule_label(top, i))  # αᴿ
            elif i > 0:  # у команд (2) и (3) переход один, и он уже испробован — возврат
                self.leave()
                continue
            elif top == H0:
                e = self.enter(pos, below, f"({self.h0_cmd})")  # команда (3)
            else:
                e = self.enter(pos + 1, below, f"({self.t_cmd[top]})")  # команда (2)
            if e == ACCEPT:
                return True
        return False

    def recognize(self, text, out):
        # Пробел — терминал только если он есть в грамматике (записан как ~). Тогда ~ во вводе
        # означает пробел. Иначе пробелы во вводе незначащие, как в примере методички «a + a*a».
        if self.has_space:
            clean = text.replace("~", " ")
            dropped = False
        else:
            clean = text.replace(" ", "").replace("\t", "")
            dropped = len(clean) != len(text)
        self.input = inp = clean

        # Сброс состояния поиска.
        # Граница высоты магазина: в кратчайшем дереве вывода на пути от корня вниз подряд идущие
        # узлы с одинаковой длиной кроны не повторяют нетерминал, поэтому глубина дерева не больше
        # (n+1)*|VN|, а каждый узел на пути держит в магазине не больше (maxRhs-1) символов.
        self.stack_limit = 2 + (len(inp) + 1) * len(self.g.nonterminals) * max(1, self.max_rhs - 1)
        self.visited = set()
        self.path = []
        self.best_path = []  # ветвь, прочитавшая больше всего символов
        self.best_same = 0   # столько первых конфигураций best_path совпадают с path
        self.best_pos = 0
        self.expected = set()      # что могло стоять во входе на позиции best_pos
        self.expected_end = False  # ... или там мог быть конец цепочки
        self.aborted = False
        self.cut_length = self.cut_count = self.cut_tail = self.cut_repeat = self.cut_stack = 0

        out.write(f"\nЦепочка: {show(inp)} (длина {screen_width(inp)})\n")
        if dropped:
            out.write("Пробелы во вводе отброшены: в грамматике нет терминала-пробела.\n")

        # Терминалы грамматики — только печатные ASCII-символы. Символ вне них (например, буква
        # кириллицы) не прочтёт ни одна команда (2), поэтому сразу отказ. Печатаем его вместе
        # с идущими следом байтами продолжения — чтобы символ UTF-8 печатался целиком.
        bad = next((k for k, ch in enumerate(inp) if not 0x20 <= ord(ch) < 0x7F), -1)
        if bad >= 0:
            stop = bad + 1
            while stop < len(inp) and "\udc80" <= inp[stop] <= "\udcbf":
                stop += 1
            out.write(f"Символ «{inp[bad:stop]}» не входит во входной алфавит P: "
                      "его не прочтёт ни одна команда (2).\n")
            out.write(f"Заключение: цепочка {show(inp)} НЕ ДОПУСКАЕТСЯ автоматом.\n")
            return False

        ok = self.search(H0 + self.g.start)

        out.write(f"Просмотрено конфигураций: {len(self.visited)}; отсечено: по длине "
                  f"{self.cut_length}, по составу {self.cut_count}, по хвосту {self.cut_tail}"
                  f", повторов {self.cut_repeat}, по высоте магазина {self.cut_stack}\n")

        if ok:
            out.write(f"Цепочка конфигураций ({tacts(len(self.path) - 1)}):\n")
            self.print_path(self.path, out)
            self.print_left_derivation(out)
            out.write(f"Заключение: цепочка {show(inp)} ДОПУСКАЕТСЯ автоматом.\n")
            return True

        if self.aborted:
            out.write(f"Поиск прерван: превышен предел в {MAX_VISITED} конфигураций.\n")
            out.write(f"Заключение: допустимость цепочки {show(inp)} не установлена.\n")
            return False

        out.write("Ни одна ветвь не дошла до заключительной конфигурации (s0, ε, ε).\n")
        out.write(f"Дальше всех продвинулась ветвь (прочитано символов: {self.best_pos} из "
                  f"{len(inp)}):\n")
        self.print_path(self.best_path, out)
        seen = f"«{show_char(inp[self.best_pos])}»" if self.best_pos < len(inp) else "конец цепочки"
        if self.expected or self.expected_end:
            # Множество печатаем по возрастанию кодов символов.
            items = [show_char(a) for a in sorted(self.expected)]
            if self.expected_end:
                items.append("конец цепочки")
            out.write(f"Ветви, дошедшие до позиции {self.best_pos + 1}, ждали там: "
                      f"{', '.join(items)}; на входе {seen}.\n")
            # Символ мог и подойти: тогда ветвь погибла не на нём, а из-за отсечения по остатку.
            if self.best_pos < len(inp) and inp[self.best_pos] in self.expected:
                out.write(f"Символ {seen} подходит, но остаток входа не согласуется с магазином "
                          "(не хватает длины, нужных терминалов или не тот конец цепочки).\n")
        start = self.g.start
        if self.min_len[start] == INF:
            out.write(f"Из {start} не выводится ни одна терминальная цепочка.\n")
        elif self.min_len[start] > len(inp):
            out.write(f"Из {start} выводятся цепочки длиной не меньше {self.min_len[start]}"
                      f", а во входе {len(inp)} симв., поэтому разбор даже не начат.\n")
        out.write(f"Заключение: цепочка {show(inp)} НЕ ДОПУСКАЕТСЯ автоматом.\n")
        return False


def main():
    # Байты, которые не складываются в UTF-8, проходят насквозь (surrogateescape), чтобы вывод
    # не ломался на любом вводе.
    sys.stdout.reconfigure(encoding="utf-8", errors="surrogateescape")
    sys.stderr.reconfigure(encoding="utf-8", errors="surrogateescape")
    if len(sys.argv) != 2:
        print(f"Использование: {sys.argv[0]} <файл грамматики>", file=sys.stderr)
        return 1

    try:
        g = read_grammar(sys.argv[1])
    except GrammarError as e:
        print(f"Ошибка в грамматике: {e}", file=sys.stderr)
        return 1

    automaton = PushdownAutomaton(g)
    automaton.print_definition(sys.stdout)

    # Цепочки читаем до пустой строки или конца ввода. Пустую цепочку вводим как ε.
    interactive = sys.stdin.isatty()
    stdin = sys.stdin.buffer
    while True:  # ЦИКЛ ввода цепочек
        if interactive:
            sys.stdout.write("\nВведите цепочку (пустая строка — выход): ")
            sys.stdout.flush()
        raw = stdin.readline()
        if not raw:
            break
        line = raw.removesuffix(b"\n").decode("utf-8", "surrogateescape")
        line = line.removesuffix("\r")
        if not line:
            break
        if line == "ε":
            line = ""
        automaton.recognize(line, sys.stdout)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
