"""Грамматика C-light как данные + FIRST, FOLLOW, таблица предиктивного анализа
M[A, a] и синхронизирующие множества для режима паники.

Всё вычисляется по алгоритмам из методички, ничего не забито руками: если
поменять продукции, таблица перестроится сама, а конфликты (две продукции
в одной ячейке, то есть грамматика не LL(1)) попадут в conflicts.

Множества — обычные set. Там, где важен порядок обхода (текст конфликтов),
обходим sorted(...): так вывод не зависит от порядка элементов в set
и одинаков от запуска к запуску.
"""

from dataclasses import dataclass, field

EPS = "ε"


@dataclass
class Production:
    """Продукция A → Y1 Y2 ... Yk. Пустой rhs означает A → ε.
    Нетерминалы пишем в угловых скобках, чтобы <for> не путался с терминалом for."""
    lhs: str
    rhs: list[str]


@dataclass
class Grammar:
    ext: bool = False                       # расширенный вариант (последовательности операторов)
    start: str = ""
    prods: list[Production] = field(default_factory=list)
    nonterminals: list[str] = field(default_factory=list)  # в порядке появления
    terminals: list[str] = field(default_factory=list)     # столбцы таблицы, последний — "$"
    first: dict[str, set[str]] = field(default_factory=dict)
    follow: dict[str, set[str]] = field(default_factory=dict)
    synch: dict[str, set[str]] = field(default_factory=dict)
    table: dict[str, dict[str, int]] = field(default_factory=dict)  # M[A][a] = индекс продукции
    conflicts: list[str] = field(default_factory=list)

    def is_nonterminal(self, s: str) -> bool:
        return s in self.first and len(s) > 1 and s[0] == "<"

    def default_production(self, A: str) -> int:
        """«Продукция по умолчанию» для пустых ячеек строки A: если у A одна продукция
        и она начинается с нетерминала, её можно раскрыть и при ошибке — тогда
        ошибку найдёт этот нетерминал, а токены не придётся выбрасывать.
        У C-light это <program> и <declaration> (обе начинаются с <type>)."""
        found = -1
        for k, p in enumerate(self.prods):
            if p.lhs == A:
                if found >= 0:
                    return -1
                found = k
        if found < 0 or not self.prods[found].rhs or not self.is_nonterminal(self.prods[found].rhs[0]):
            return -1
        return found

    def cell(self, A: str, a: str) -> int:
        """M[A, a]: индекс продукции или -1, если ячейка пуста (ошибка)."""
        return self.table.get(A, {}).get(a, -1)

    def first_of(self, seq: list[str]) -> set[str]:
        """FIRST цепочки X1 X2 ... Xn (правило из методички): берём FIRST(X1) без ε,
        если X1 ⇒* ε — добавляем FIRST(X2) и т.д.; ε — только если все Xi ⇒* ε."""
        res = set()
        for x in seq:  # ЦИКЛ по символам цепочки
            if not self.is_nonterminal(x):  # терминал: FIRST(a) = {a}, дальше не смотрим
                res.add(x)
                return res
            f = self.first[x]
            res |= f - {EPS}
            if EPS not in f:  # РАЗВИЛКА: Xi не порождает ε — стоп
                return res
        res.add(EPS)
        return res

    def production_text(self, k: int) -> str:
        p = self.prods[k]
        r = p.lhs + " →"
        if not p.rhs:
            r += " " + EPS
        for x in p.rhs:
            r += " " + x
        return r


def make_grammar(ext: bool) -> Grammar:
    """Грамматика C-light на уровне токенов. Это ровно грамматика из методички,
    только <identifier> и <number> стали терминалами id и num (их распознаёт
    лексер), а пробельные символы между токенами съедает тот же лексер.

    ext = True — небольшое расширение (флаг --ext): в блоке { } может стоять
    последовательность операторов, пустой оператор пишется как ';'."""
    g = Grammar(ext=ext, start="<program>")

    def P(lhs, rhs):
        g.prods.append(Production(lhs, rhs))

    body = "<stmts>" if ext else "<statement>"

    P("<program>", ["<type>", "main", "(", ")", "{", body, "}"])
    P("<type>", ["int"])
    P("<type>", ["bool"])
    P("<type>", ["void"])
    if ext:
        P("<stmts>", ["<statement>", "<stmts>"])
        P("<stmts>", [])
    else:
        P("<statement>", [])  # <statement> может быть пустым
    P("<statement>", ["<declaration>", ";"])
    P("<statement>", ["{", body, "}"])
    P("<statement>", ["<for>", "<statement>"])
    P("<statement>", ["<if>", "<statement>"])
    P("<statement>", ["<return>"])
    if ext:
        P("<statement>", [";"])
    P("<declaration>", ["<type>", "id", "<assign>"])
    P("<assign>", [])
    P("<assign>", ["=", "<assign_end>"])
    P("<assign_end>", ["id"])
    P("<assign_end>", ["num"])
    P("<for>", ["for", "(", "<declaration>", ";", "<bool_expression>", ";", ")"])
    P("<bool_expression>", ["id", "<relop>", "id"])
    P("<bool_expression>", ["num", "<relop>", "id"])
    P("<relop>", ["<"])
    P("<relop>", [">"])
    P("<relop>", ["=="])
    P("<relop>", ["!="])
    P("<if>", ["if", "(", "<bool_expression>", ")"])
    P("<return>", ["return", "num", ";"])

    g.terminals = ["int", "bool", "void", "main", "for", "if", "return", "(", ")", "{",
                   "}", ";", "=", "<", ">", "==", "!=", "id", "num", "$"]
    for p in g.prods:
        if p.lhs not in g.first:
            g.nonterminals.append(p.lhs)
            g.first[p.lhs] = set()  # пустое множество — по нему is_nonterminal узнаёт нетерминал
    return g


def build_tables(g: Grammar) -> None:
    """Строит FIRST, FOLLOW, таблицу M и synch-множества."""
    # --- FIRST: повторяем правила, пока хоть одно множество растёт.
    changed = True
    while changed:  # ЦИКЛ до неподвижной точки
        changed = False
        for p in g.prods:
            f = g.first_of(p.rhs)  # для A → ε даёт {ε}
            dst = g.first[p.lhs]
            if not f <= dst:
                dst |= f
                changed = True

    # --- FOLLOW: $ в FOLLOW(S); для A → αBβ: FIRST(β)\{ε} в FOLLOW(B),
    # а если β ⇒* ε — ещё и весь FOLLOW(A).
    for A in g.nonterminals:
        g.follow[A] = set()
    g.follow[g.start].add("$")
    changed = True
    while changed:  # ЦИКЛ до неподвижной точки
        changed = False
        for p in g.prods:
            for i, B in enumerate(p.rhs):
                if not g.is_nonterminal(B):
                    continue
                f = g.first_of(p.rhs[i + 1:])
                add = f - {EPS}
                if EPS in f:  # РАЗВИЛКА: хвост β может исчезнуть
                    add |= g.follow[p.lhs]
                dst = g.follow[B]
                if not add <= dst:
                    dst |= add
                    changed = True

    # --- Таблица M: A → α кладём в M[A,a] для a ∈ FIRST(α),
    # а если ε ∈ FIRST(α) — ещё в M[A,b] для b ∈ FOLLOW(A).
    def put(A, a, k):
        row = g.table.setdefault(A, {})
        old = row.setdefault(a, k)
        if old != k:
            g.conflicts.append(f"M[{A}, {a}]: продукции {old + 1} и {k + 1}")

    for k, p in enumerate(g.prods):
        f = g.first_of(p.rhs)
        for a in sorted(f):
            if a != EPS:
                put(p.lhs, a, k)
        if EPS in f:
            for b in sorted(g.follow[p.lhs]):
                put(p.lhs, b, k)

    # --- Синхронизирующие множества (режим паники), эвристики из методички:
    # 1) FOLLOW(A) — после A обычно идёт что-то из FOLLOW(A);
    # 2) для конструкций ниже уровня оператора добавляем символы, с которых
    #    начинается оператор, и '}' — иначе пропущенная ';' перед "if"
    #    заставит выбросить весь следующий оператор;
    # 3) FIRST(A) добавлять не нужно: на этих символах в M[A,a] уже стоит продукция.
    stmt_first = set(g.first["<statement>"])
    for A in g.nonterminals:
        s = set(g.follow[A])
        s.add("$")
        if A not in ("<program>", "<statement>", "<stmts>"):
            s |= stmt_first - {EPS}
            s.add("}")
        g.synch[A] = s
