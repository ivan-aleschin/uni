// Реализация классов из automaton.h.
#include "automaton.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <queue>
#include <sstream>
#include <stdexcept>

// ---------- символы ----------

// Сколько байт занимает символ, начинающийся в s с позиции i.
// Правильный UTF-8 (русская буква — 2 байта) — один символ. Если байты не
// складываются в UTF-8 (файл в cp1251), каждый байт считаем отдельным символом,
// иначе "q0,<буква cp1251>=f0" съел бы '=' как хвост буквы.
static size_t symLen(const std::string& s, size_t i) {
    unsigned char c = static_cast<unsigned char>(s[i]);
    size_t len = c < 0x80 ? 1 : (c & 0xE0) == 0xC0 ? 2 : (c & 0xF0) == 0xE0 ? 3 : (c & 0xF8) == 0xF0 ? 4 : 1;
    if (i + len > s.size()) return 1;
    for (size_t k = 1; k < len; ++k)
        if ((static_cast<unsigned char>(s[i + k]) & 0xC0) != 0x80) return 1;  // не байт-продолжение
    return len;
}

std::vector<Symbol> splitSymbols(const std::string& s) {
    std::vector<Symbol> out;
    for (size_t i = 0; i < s.size();) {
        size_t len = symLen(s, i);
        out.push_back(s.substr(i, len));
        i += len;
    }
    return out;
}

// Ширина строки на экране: считаем символы, а не байты (для таблицы).
static size_t displayWidth(const std::string& s) { return splitSymbols(s).size(); }

std::string showSym(const Symbol& s) {
    if (s == "\t") return "'\\t'";
    if (s.size() == 1 && static_cast<unsigned char>(s[0]) < 0x20) {
        char buf[16];
        std::snprintf(buf, sizeof buf, "'\\x%02X'", static_cast<unsigned char>(s[0]));
        return buf;
    }
    return "'" + s + "'";
}

std::string showSet(const StateSet& set) {
    std::string out = "{";
    for (const State& s : set) out += (out.size() > 1 ? ", " : "") + s.name();
    return out + "}";
}

// ---------- чтение файла ----------

// Читает номер состояния начиная с pos. false — цифр нет или их слишком много.
// До 18 цифр помещается в long long с запасом: новые номера состояний ДКА
// (максимум + 1, + 2, ...) не переполнятся и прочитаются обратно.
static bool readNumber(const std::string& s, size_t& pos, long long& num) {
    size_t start = pos;
    while (pos < s.size() && std::isdigit(static_cast<unsigned char>(s[pos]))) ++pos;
    if (pos == start || pos - start > 18) return false;
    num = std::stoll(s.substr(start, pos - start));
    return true;
}

// Буква состояния: q — обычное, f — конечное (регистр не важен, как у преподавателя).
static bool readStateLetter(char c, bool& final) {
    if (c == 'q' || c == 'Q') { final = false; return true; }
    if (c == 'f' || c == 'F') { final = true; return true; }
    return false;
}

static std::string quoteChar(const std::string& s, size_t pos) {
    return pos < s.size() ? showSym(splitSymbols(s.substr(pos))[0]) : "конец строки";
}

bool RuleFileReader::parseLine(const std::string& line, Rule& rule, std::string& err) {
    size_t pos = 0;

    // 1. Исходное состояние: q<N> (f<N> тоже разрешаем — так записывает ДКА наша программа)
    if (!readStateLetter(line[pos], rule.from.final)) {
        err = "строка должна начинаться с 'q' (или 'f'), а начинается с " + quoteChar(line, pos);
        return false;
    }
    ++pos;
    if (!readNumber(line, pos, rule.from.num)) {
        err = "после '" + line.substr(0, 1) + "' нет номера состояния (или он длиннее 18 цифр)";
        return false;
    }

    // 2. Запятая
    if (pos >= line.size() || line[pos] != ',') {
        err = "после номера состояния ожидалась ',', а стоит " + quoteChar(line, pos);
        return false;
    }
    ++pos;

    // 3. Ровно один символ — любой, включая пробел, ',', '=' и ';'
    if (pos >= line.size()) {
        err = "после ',' нет символа перехода";
        return false;
    }
    size_t len = symLen(line, pos);
    rule.sym = line.substr(pos, len);
    pos += len;

    // 4. Знак '='
    if (pos >= line.size() || line[pos] != '=') {
        // Частый случай: "q1,=q2" — забыли символ (переходов по пустому символу в формате нет)
        bool dummy;
        if (rule.sym == "=" && pos < line.size() && readStateLetter(line[pos], dummy))
            err = "после ',' сразу '=' — нет символа перехода (ε-переходы формат не допускает)";
        else
            err = "после символа " + showSym(rule.sym) + " ожидался '=', а стоит " +
                  quoteChar(line, pos) + " (символ перехода должен быть ровно один)";
        return false;
    }
    ++pos;

    // 5. Целевое состояние q<N> или f<N>
    if (pos >= line.size() || !readStateLetter(line[pos], rule.to.final)) {
        err = "после '=' ожидалось состояние q<N> или f<N>, а стоит " + quoteChar(line, pos);
        return false;
    }
    const std::string letter = line.substr(pos++, 1);  // q или f — для сообщения об ошибке
    if (!readNumber(line, pos, rule.to.num)) {
        err = "после '" + letter + "' нет номера состояния (или он длиннее 18 цифр)";
        return false;
    }

    // 6. После номера ничего быть не должно
    if (pos != line.size()) {
        err = "лишние символы после номера состояния: '" + line.substr(pos) + "'";
        return false;
    }
    return true;
}

RuleFileReader::RuleFileReader(const std::string& path) {
    std::ifstream in(path);
    if (!in.is_open()) throw std::runtime_error("не удалось открыть файл " + path);

    std::string raw;
    while (std::getline(in, raw)) {
        ++totalLines_;
        // Блокнот Windows может записать в начало файла метку UTF-8 (BOM) —
        // без этого первое правило (обычно из q0) стало бы ошибкой.
        if (totalLines_ == 1 && raw.starts_with("\xEF\xBB\xBF")) raw.erase(0, 3);
        // Файлы преподавателя в формате Windows: убираем '\r' в конце.
        // Пробелы по краям тоже срезаем — символ перехода стоит в середине
        // строки, так что пробел-символ ("q3, =q3") от этого не пострадает.
        std::string line = raw;
        while (!line.empty() && std::isspace(static_cast<unsigned char>(line.back()))) line.pop_back();
        size_t first = 0;
        while (first < line.size() && std::isspace(static_cast<unsigned char>(line[first]))) ++first;
        line.erase(0, first);

        // Пустые строки и комментарии (с ';' или '#') пропускаем.
        // Правило всегда начинается с q/f, поэтому путаницы с символом ';' нет.
        if (line.empty() || line[0] == ';' || line[0] == '#') {
            ++skippedLines_;
            continue;
        }

        Rule rule;
        std::string err;
        if (parseLine(line, rule, err)) {
            rule.line = totalLines_;
            rules_.push_back(rule);
        } else {
            errors_.push_back({totalLines_, line, err});  // запоминаем и читаем дальше
        }
    }
}

// ---------- автомат ----------

FiniteAutomaton::FiniteAutomaton(const std::vector<Rule>& rules) {
    for (const Rule& r : rules) addRule(r);
}

bool FiniteAutomaton::addRule(const Rule& r) {
    StateSet& to = delta_[r.from][r.sym];
    if (to.contains(r.to)) {  // РАЗВИЛКА: точно такое же правило уже есть
        duplicates_.push_back(r);
        return false;
    }
    to.insert(r.to);
    rules_.push_back(r);
    allStates_.insert(r.from);
    allStates_.insert(r.to);
    return true;
}

StateSet FiniteAutomaton::states() const {
    StateSet s = allStates_;
    s.insert(kStart);  // q0 есть всегда, даже если в файле его забыли
    return s;
}

StateSet FiniteAutomaton::finals() const {
    StateSet s;
    for (const State& st : allStates_)
        if (st.final) s.insert(st);
    return s;
}

std::set<Symbol> FiniteAutomaton::alphabet() const {
    std::set<Symbol> a;
    for (const Rule& r : rules_) a.insert(r.sym);
    return a;
}

StateSet FiniteAutomaton::targets(const State& state, const Symbol& sym) const {
    auto it = delta_.find(state);
    if (it == delta_.end()) return {};
    auto jt = it->second.find(sym);
    return jt == it->second.end() ? StateSet{} : jt->second;
}

std::vector<Symbol> FiniteAutomaton::expectedSymbols(const State& state) const {
    std::vector<Symbol> out;
    auto it = delta_.find(state);
    if (it != delta_.end())
        for (const auto& [sym, to] : it->second) out.push_back(sym);
    return out;
}

std::vector<Conflict> FiniteAutomaton::conflicts() const {
    // Собираем правила по паре (состояние, символ). Дубликаты уже отброшены,
    // значит, два правила в одной группе ведут в разные состояния.
    std::map<std::pair<State, Symbol>, std::vector<Rule>> groups;
    for (const Rule& r : rules_) groups[{r.from, r.sym}].push_back(r);

    std::vector<Conflict> out;
    for (const auto& [key, rules] : groups)
        if (rules.size() > 1) out.push_back({key.first, key.second, rules});
    return out;
}

StateSet FiniteAutomaton::unreachable() const {
    // Обход в ширину от q0 по направлению стрелок.
    StateSet seen{kStart};
    std::queue<State> q;
    q.push(kStart);
    while (!q.empty()) {  // ЦИКЛ: пока есть необработанные состояния
        State cur = q.front();
        q.pop();
        auto it = delta_.find(cur);
        if (it == delta_.end()) continue;
        for (const auto& [sym, to] : it->second)
            for (const State& t : to)
                if (seen.insert(t).second) q.push(t);
    }
    StateSet out;
    for (const State& s : states())
        if (!seen.contains(s)) out.insert(s);
    return out;
}

StateSet FiniteAutomaton::dead() const {
    // Обход в ширину от всех конечных состояний против стрелок:
    // кого посетили — из того конечное достижимо.
    std::map<State, StateSet> reverse;
    for (const Rule& r : rules_) reverse[r.to].insert(r.from);

    StateSet seen = finals();
    std::queue<State> q;
    for (const State& f : seen) q.push(f);
    while (!q.empty()) {  // ЦИКЛ: обход назад от конечных
        State cur = q.front();
        q.pop();
        for (const State& prev : reverse[cur])
            if (seen.insert(prev).second) q.push(prev);
    }
    StateSet out;
    for (const State& s : states())
        if (!seen.contains(s)) out.insert(s);
    return out;
}

Determinized FiniteAutomaton::determinize() const {
    Determinized res;

    // Новые составные состояния получают номера после самых больших старых,
    // чтобы не совпасть ни с одним старым именем. Одиночные множества {qK}
    // сохраняют старое имя qK — так ДКА легче сверять с исходным графом.
    long long nextQ = 0, nextF = 0;
    for (const State& s : states()) {
        if (s.final) nextF = std::max(nextF, s.num + 1);
        else nextQ = std::max(nextQ, s.num + 1);
    }

    std::map<StateSet, State> names;  // множество старых состояний -> новое состояние
    std::queue<StateSet> todo;

    // Имя для множества; новое множество сразу ставим в очередь на обработку.
    auto nameOf = [&](const StateSet& set) -> State {
        auto it = names.find(set);
        if (it != names.end()) return it->second;
        State n;
        if (set.size() == 1) {
            n = *set.begin();
        } else {
            // Множество конечное, если в нём есть хоть одно конечное состояние.
            bool fin = std::any_of(set.begin(), set.end(), [](const State& s) { return s.final; });
            n = fin ? State{true, nextF++} : State{false, nextQ++};
        }
        names[set] = n;
        res.composition.push_back({n, set});
        todo.push(set);
        return n;
    };

    nameOf({kStart});
    while (!todo.empty()) {  // ЦИКЛ: пока есть необработанные множества
        StateSet cur = todo.front();
        todo.pop();
        // t(q', a) = объединение t(q, a) по всем q из q'
        std::map<Symbol, StateSet> moves;
        for (const State& s : cur) {
            auto it = delta_.find(s);
            if (it == delta_.end()) continue;
            for (const auto& [sym, to] : it->second) moves[sym].insert(to.begin(), to.end());
        }
        State from = names.at(cur);
        for (const auto& [sym, to] : moves) res.dfa.addRule({from, sym, nameOf(to), 0});
    }
    return res;
}

RunResult FiniteAutomaton::run(const std::string& input) const {
    RunResult res;
    res.input = splitSymbols(input);
    State cur = kStart;
    res.path.push_back(cur);

    auto expected = [&](const State& s) {
        std::string out;
        for (const Symbol& sym : expectedSymbols(s)) out += (out.empty() ? "" : ", ") + showSym(sym);
        return out;
    };

    for (size_t i = 0; i < res.input.size(); ++i) {  // ЦИКЛ: по символам строки
        const Symbol& sym = res.input[i];
        StateSet next = targets(cur, sym);
        if (next.size() > 1) throw std::logic_error("run() вызван для недетерминированного автомата");
        if (next.empty()) {  // РАЗВИЛКА: перехода нет — строка отвергнута
            std::ostringstream why;
            why << "символ №" << i + 1 << " " << showSym(sym) << ": ";
            if (!hasOutgoing(cur))
                why << "из " << cur.name() << " переходов нет вообще, строка должна была здесь закончиться";
            else
                why << "из " << cur.name() << " по нему перехода нет, ожидалось: " << expected(cur);
            if (!alphabet().contains(sym)) why << " (символа " << showSym(sym) << " нет в алфавите)";
            res.reason = why.str();
            return res;
        }
        cur = *next.begin();
        res.path.push_back(cur);
    }

    res.accepted = cur.final;  // строка кончилась: допуск, если стоим в конечном состоянии
    if (!res.accepted) {
        if (res.input.empty())
            res.reason = "пустая строка: q0 не конечное состояние";
        else
            res.reason = "строка закончилась в состоянии " + cur.name() +
                         ", оно не конечное" + (hasOutgoing(cur) ? "; дальше ожидалось: " + expected(cur) : "");
    }
    return res;
}

bool FiniteAutomaton::runNfa(const std::string& input) const {
    // Держим множество всех состояний, в которых НКА может оказаться.
    StateSet cur{kStart};
    for (const Symbol& sym : splitSymbols(input)) {  // ЦИКЛ: по символам строки
        StateSet next;
        for (const State& s : cur) {
            StateSet t = targets(s, sym);
            next.insert(t.begin(), t.end());
        }
        if (next.empty()) return false;
        cur = std::move(next);
    }
    return std::any_of(cur.begin(), cur.end(), [](const State& s) { return s.final; });
}

// ---------- вывод ----------

void FiniteAutomaton::printRules(std::ostream& out) const {
    for (const Rule& r : rules_) out << r.from.name() << ',' << r.sym << '=' << r.to.name() << '\n';
}

void FiniteAutomaton::printTable(std::ostream& out) const {
    const std::set<Symbol> alpha = alphabet();
    const StateSet all = states();
    const std::vector<Symbol> syms(alpha.begin(), alpha.end());
    const std::vector<State> rows(all.begin(), all.end());

    // Текст каждой клетки: '-' (перехода нет), qK или {qA,qB} у НКА.
    auto cell = [&](const State& s, const Symbol& sym) -> std::string {
        StateSet t = targets(s, sym);
        if (t.empty()) return "-";
        if (t.size() == 1) return t.begin()->name();
        std::string str;
        for (const State& x : t) str += (str.empty() ? "" : ",") + x.name();
        return "{" + str + "}";
    };
    auto rowLabel = [&](const State& s) {
        return std::string(s == kStart ? "->" : "  ") + (s.final ? "*" : " ") + s.name();
    };

    size_t labelW = 0;
    for (const State& s : rows) labelW = std::max(labelW, rowLabel(s).size());
    std::vector<size_t> w(syms.size());
    for (size_t j = 0; j < syms.size(); ++j) {
        w[j] = displayWidth(showSym(syms[j]));
        for (const State& s : rows) w[j] = std::max(w[j], cell(s, syms[j]).size());
    }
    auto pad = [](const std::string& s, size_t width) {
        return s + std::string(width - std::min(width, displayWidth(s)), ' ');
    };

    out << pad("", labelW);
    for (size_t j = 0; j < syms.size(); ++j) out << " | " << pad(showSym(syms[j]), w[j]);
    out << '\n' << std::string(labelW, '-');
    for (size_t j = 0; j < syms.size(); ++j) out << "-+-" << std::string(w[j], '-');
    out << '\n';
    for (const State& s : rows) {  // ЦИКЛ: строка таблицы на каждое состояние
        std::string row = pad(rowLabel(s), labelW);
        for (size_t j = 0; j < syms.size(); ++j) row += " | " + pad(cell(s, syms[j]), w[j]);
        while (row.back() == ' ') row.pop_back();  // без хвостовых пробелов
        out << row << '\n';
    }
}

// Экранирование текста для подписи в DOT.
static std::string dotEscape(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '"' || c == '\\') out += '\\';
        out += c;
    }
    return out;
}

void FiniteAutomaton::writeDot(std::ostream& out, const std::string& title,
                               const std::map<State, StateSet>& composition) const {
    StateSet unreach = unreachable(), deadSet = dead();

    out << "digraph \"" << dotEscape(title) << "\" {\n"
        << "  rankdir=LR;\n"
        << "  label=\"" << dotEscape(title) << "\"; labelloc=t; fontname=\"Helvetica\";\n"
        << "  node [shape=circle, fontname=\"Helvetica\"];\n"
        << "  edge [fontname=\"Helvetica\"];\n"
        << "  start [shape=point];\n"
        << "  start -> q0;\n";

    // Вершины: конечные — прямоугольником, как на рисунках методички.
    for (const State& s : states()) {
        std::string label = s.name();
        auto it = composition.find(s);
        if (it != composition.end() && it->second.size() > 1) label += "\\n" + showSet(it->second);
        out << "  " << s.name() << " [label=\"" << label << "\"";
        if (s.final) out << ", shape=box";
        if (unreach.contains(s)) out << ", style=dashed, color=gray, fontcolor=gray";
        else if (deadSet.contains(s)) out << ", color=red, fontcolor=red";
        out << "];\n";
    }

    // Рёбра: все символы между одной парой состояний — одной стрелкой.
    std::map<std::pair<State, State>, std::string> edges;
    for (const Rule& r : rules_) {
        std::string& lbl = edges[{r.from, r.to}];
        lbl += (lbl.empty() ? "" : " ") + showSym(r.sym);
    }
    for (const auto& [ft, lbl] : edges)
        out << "  " << ft.first.name() << " -> " << ft.second.name() << " [label=\"" << dotEscape(lbl) << "\"];\n";
    out << "}\n";
}
