// Грамматика C-light как данные + FIRST, FOLLOW, таблица предиктивного анализа
// M[A, a] и синхронизирующие множества для режима паники.
//
// Всё вычисляется по алгоритмам из методички, ничего не забито руками: если
// поменять продукции, таблица перестроится сама, а конфликты (две продукции
// в одной ячейке, то есть грамматика не LL(1)) попадут в conflicts.
#pragma once

#include <map>
#include <set>
#include <string>
#include <vector>

inline const std::string EPS = "ε";

// Продукция A → Y1 Y2 ... Yk. Пустой rhs означает A → ε.
// Нетерминалы пишем в угловых скобках, чтобы <for> не путался с терминалом for.
struct Production {
    std::string lhs;
    std::vector<std::string> rhs;
};

struct Grammar {
    bool ext = false;                       // расширенный вариант (последовательности операторов)
    std::string start;
    std::vector<Production> prods;
    std::vector<std::string> nonterminals;  // в порядке появления
    std::vector<std::string> terminals;     // столбцы таблицы, последний — "$"
    std::map<std::string, std::set<std::string>> first, follow, synch;
    std::map<std::string, std::map<std::string, int>> table;  // M[A][a] = индекс продукции
    std::vector<std::string> conflicts;

    bool isNonterminal(const std::string& s) const { return first.count(s) && s.size() > 1 && s[0] == '<'; }

    // «Продукция по умолчанию» для пустых ячеек строки A: если у A одна продукция
    // и она начинается с нетерминала, её можно раскрыть и при ошибке — тогда
    // ошибку найдёт этот нетерминал, а токены не придётся выбрасывать.
    // У C-light это <program> и <declaration> (обе начинаются с <type>).
    // У <for>, <if>, <return> продукция начинается с ключевого слова, и
    // в их строку анализатор попадает только по этому слову — там не нужно.
    int defaultProduction(const std::string& A) const {
        int found = -1;
        for (int k = 0; k < static_cast<int>(prods.size()); ++k)
            if (prods[k].lhs == A) {
                if (found >= 0) return -1;
                found = k;
            }
        if (found < 0 || prods[found].rhs.empty() || !isNonterminal(prods[found].rhs[0])) return -1;
        return found;
    }

    // M[A, a]: индекс продукции или -1, если ячейка пуста (ошибка).
    int cell(const std::string& A, const std::string& a) const {
        auto row = table.find(A);
        if (row == table.end()) return -1;
        auto it = row->second.find(a);
        return it == row->second.end() ? -1 : it->second;
    }

    // FIRST цепочки X1 X2 ... Xn (правило из методички): берём FIRST(X1) без ε,
    // если X1 ⇒* ε — добавляем FIRST(X2) и т.д.; ε — только если все Xi ⇒* ε.
    template <class It>
    std::set<std::string> firstOf(It b, It e) const {
        std::set<std::string> res;
        for (It it = b; it != e; ++it) {  // ЦИКЛ по символам цепочки
            if (!isNonterminal(*it)) {    // терминал: FIRST(a) = {a}, дальше не смотрим
                res.insert(*it);
                return res;
            }
            const auto& f = first.at(*it);
            for (const auto& x : f)
                if (x != EPS) res.insert(x);
            if (!f.count(EPS)) return res;  // РАЗВИЛКА: Xi не порождает ε — стоп
        }
        res.insert(EPS);
        return res;
    }
    std::set<std::string> firstOf(const std::vector<std::string>& seq) const {
        return firstOf(seq.begin(), seq.end());
    }

    std::string productionText(int k) const {
        const auto& p = prods[k];
        std::string r = p.lhs + " →";
        if (p.rhs.empty()) r += " " + EPS;
        for (const auto& x : p.rhs) r += " " + x;
        return r;
    }
};

// Грамматика C-light на уровне токенов. Это ровно грамматика из методички,
// только <identifier> и <number> стали терминалами id и num (их распознаёт
// лексер), а пробельные символы между токенами съедает тот же лексер.
//
// ext = true — небольшое расширение (флаг --ext): в блоке { } может стоять
// последовательность операторов, пустой оператор пишется как ';'.
inline Grammar makeGrammar(bool ext) {
    Grammar g;
    g.ext = ext;
    g.start = "<program>";
    auto P = [&](const std::string& lhs, std::vector<std::string> rhs) { g.prods.push_back({lhs, std::move(rhs)}); };
    const std::string body = ext ? "<stmts>" : "<statement>";

    P("<program>", {"<type>", "main", "(", ")", "{", body, "}"});
    P("<type>", {"int"});
    P("<type>", {"bool"});
    P("<type>", {"void"});
    if (ext) {
        P("<stmts>", {"<statement>", "<stmts>"});
        P("<stmts>", {});
    } else {
        P("<statement>", {});  // <statement> может быть пустым
    }
    P("<statement>", {"<declaration>", ";"});
    P("<statement>", {"{", body, "}"});
    P("<statement>", {"<for>", "<statement>"});
    P("<statement>", {"<if>", "<statement>"});
    P("<statement>", {"<return>"});
    if (ext) P("<statement>", {";"});
    P("<declaration>", {"<type>", "id", "<assign>"});
    P("<assign>", {});
    P("<assign>", {"=", "<assign_end>"});
    P("<assign_end>", {"id"});
    P("<assign_end>", {"num"});
    P("<for>", {"for", "(", "<declaration>", ";", "<bool_expression>", ";", ")"});
    P("<bool_expression>", {"id", "<relop>", "id"});
    P("<bool_expression>", {"num", "<relop>", "id"});
    P("<relop>", {"<"});
    P("<relop>", {">"});
    P("<relop>", {"=="});
    P("<relop>", {"!="});
    P("<if>", {"if", "(", "<bool_expression>", ")"});
    P("<return>", {"return", "num", ";"});

    g.terminals = {"int", "bool", "void", "main", "for", "if", "return", "(", ")", "{",
                   "}", ";", "=", "<", ">", "==", "!=", "id", "num", "$"};
    for (const auto& p : g.prods) {
        if (!g.first.count(p.lhs)) {
            g.nonterminals.push_back(p.lhs);
            g.first[p.lhs];  // заводим пустое множество — по нему isNonterminal узнаёт нетерминал
        }
    }
    return g;
}

// Строит FIRST, FOLLOW, таблицу M и synch-множества.
inline void buildTables(Grammar& g) {
    // --- FIRST: повторяем правила, пока хоть одно множество растёт.
    for (bool changed = true; changed;) {  // ЦИКЛ до неподвижной точки
        changed = false;
        for (const auto& p : g.prods) {
            auto f = g.firstOf(p.rhs);  // для A → ε даёт {ε}
            auto& dst = g.first[p.lhs];
            for (const auto& x : f) changed |= dst.insert(x).second;
        }
    }

    // --- FOLLOW: $ в FOLLOW(S); для A → αBβ: FIRST(β)\{ε} в FOLLOW(B),
    // а если β ⇒* ε — ещё и весь FOLLOW(A).
    for (const auto& A : g.nonterminals) g.follow[A];
    g.follow[g.start].insert("$");
    for (bool changed = true; changed;) {  // ЦИКЛ до неподвижной точки
        changed = false;
        for (const auto& p : g.prods) {
            for (size_t i = 0; i < p.rhs.size(); ++i) {
                const auto& B = p.rhs[i];
                if (!g.isNonterminal(B)) continue;
                auto f = g.firstOf(p.rhs.begin() + i + 1, p.rhs.end());
                auto& dst = g.follow[B];
                for (const auto& x : f)
                    if (x != EPS) changed |= dst.insert(x).second;
                if (f.count(EPS))  // РАЗВИЛКА: хвост β может исчезнуть
                    for (const auto& x : g.follow[p.lhs]) changed |= dst.insert(x).second;
            }
        }
    }

    // --- Таблица M: A → α кладём в M[A,a] для a ∈ FIRST(α),
    // а если ε ∈ FIRST(α) — ещё в M[A,b] для b ∈ FOLLOW(A).
    auto put = [&](const std::string& A, const std::string& a, int k) {
        auto [it, inserted] = g.table[A].emplace(a, k);
        if (!inserted && it->second != k)
            g.conflicts.push_back("M[" + A + ", " + a + "]: продукции " + std::to_string(it->second + 1) +
                                  " и " + std::to_string(k + 1));
    };
    for (int k = 0; k < static_cast<int>(g.prods.size()); ++k) {
        const auto& p = g.prods[k];
        auto f = g.firstOf(p.rhs);
        for (const auto& a : f)
            if (a != EPS) put(p.lhs, a, k);
        if (f.count(EPS))
            for (const auto& b : g.follow[p.lhs]) put(p.lhs, b, k);
    }

    // --- Синхронизирующие множества (режим паники), эвристики из методички:
    // 1) FOLLOW(A) — после A обычно идёт что-то из FOLLOW(A);
    // 2) для конструкций ниже уровня оператора добавляем символы, с которых
    //    начинается оператор, и '}' — иначе пропущенная ';' перед "if"
    //    заставит выбросить весь следующий оператор;
    // 3) FIRST(A) добавлять не нужно: на этих символах в M[A,a] уже стоит продукция.
    const auto stmtFirst = g.first["<statement>"];
    for (const auto& A : g.nonterminals) {
        auto& s = g.synch[A];
        s = g.follow[A];
        s.insert("$");
        if (A != "<program>" && A != "<statement>" && A != "<stmts>") {
            for (const auto& x : stmtFirst)
                if (x != EPS) s.insert(x);
            s.insert("}");
        }
    }
}
