// ЛР3 по ТАЯК: недетерминированный магазинный (МП) автомат, построенный по КС-грамматике.
//
// Программа читает грамматику из файла, строит по ней автомат так, как описано в методичке
// (одно состояние s0, команды (1)-(4)), печатает его описание, а потом для каждой введённой
// цепочки ищет последовательность тактов, приводящую в заключительную конфигурацию.
// Автомат недетерминированный, поэтому поиск идёт с возвратом (перебор в глубину).

#include <algorithm>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <unordered_set>
#include <vector>

namespace {

// Маркер дна магазина h0. В файле грамматики управляющих символов быть не может,
// поэтому \x01 ни с одним терминалом не совпадёт.
constexpr char H0 = '\x01';
// «Бесконечная» длина — для нетерминалов, из которых не выводится ни одна терминальная цепочка.
constexpr std::size_t INF = std::numeric_limits<std::size_t>::max();
// Предохранитель: больше стольких конфигураций за один разбор не просматриваем.
constexpr std::size_t MAX_VISITED = 2'000'000;

bool isNonterminal(char c) { return c >= 'A' && c <= 'Z'; }

// Как символ показывается человеку: пробел — как ~ (так же он задаётся в файле), дно — как h0.
std::string show(char c) {
    if (c == H0) return "h0";
    if (c == ' ') return "~";
    return std::string(1, c);
}

// Цепочка символов для печати; пустая цепочка печатается как ε.
std::string show(const std::string& s) {
    if (s.empty()) return "ε";
    std::string out;
    for (char c : s) out += show(c);
    return out;
}

// Длина строки в «знаках» на экране: байты продолжения UTF-8 (10xxxxxx) не считаем.
std::size_t screenWidth(const std::string& s) {
    return static_cast<std::size_t>(std::count_if(s.begin(), s.end(),
        [](char c) { return (static_cast<unsigned char>(c) & 0xC0) != 0x80; }));
}

// «1 такт», «3 такта», «12 тактов».
std::string tacts(std::size_t n) {
    std::size_t d10 = n % 10, d100 = n % 100;
    const char* word = (d10 == 1 && d100 != 11)                           ? "такт"
                       : (d10 >= 2 && d10 <= 4 && (d100 < 12 || d100 > 14)) ? "такта"
                                                                            : "тактов";
    return std::to_string(n) + " " + word;
}

std::size_t addSat(std::size_t a, std::size_t b) { return (a == INF || b == INF) ? INF : a + b; }

// ---------------------------------------------------------------------------------------------
// Грамматика и её чтение из файла
// ---------------------------------------------------------------------------------------------

struct Grammar {
    char start = 0;                                  // I — левая часть первого правила
    std::vector<char> nonterminals;                  // VN в порядке появления левых частей
    std::vector<char> terminals;                     // VT в порядке первого появления
    std::map<char, std::vector<std::string>> rules;  // A -> список правых частей ("" = ε)
};

struct GrammarError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

GrammarError errorAt(int lineNo, const std::string& msg) {
    return GrammarError("строка " + std::to_string(lineNo) + ": " + msg);
}

Grammar readGrammar(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw GrammarError("не удалось открыть файл «" + path + "»");

    Grammar g;
    std::vector<std::pair<char, int>> usedOnRight;  // нетерминалы из правых частей и номер строки
    std::string line;
    int lineNo = 0;
    while (std::getline(in, line)) {
        ++lineNo;
        // Пробелы, табуляции и \r (файлы преподавателя сохранены в Windows) незначащие.
        std::string s;
        for (char c : line)
            if (c != ' ' && c != '\t' && c != '\r') s += c;
        if (s.empty()) continue;  // пустые строки просто пропускаем

        for (char c : s) {
            auto u = static_cast<unsigned char>(c);
            if (u < 0x20 || u >= 0x7F)
                throw errorAt(lineNo, "допустимы только печатные ASCII-символы "
                                      "(пробел-терминал записывается как ~)");
        }

        // Первый '>' отделяет левую часть от правой, остальные '>' — обычные терминалы.
        std::size_t arrow = s.find('>');
        if (arrow == std::string::npos)
            throw errorAt(lineNo, "нет символа '>', отделяющего левую часть правила от правой");
        std::string left = s.substr(0, arrow);
        if (left.size() != 1 || !isNonterminal(left[0]))
            throw errorAt(lineNo, "левая часть «" + left + "» должна быть одной заглавной "
                                  "латинской буквой");
        char A = left[0];
        if (g.start == 0) g.start = A;
        if (!g.rules.count(A)) g.nonterminals.push_back(A);

        // Правая часть делится по '|'; пустая альтернатива означает ε-правило A -> ε.
        std::string right = s.substr(arrow + 1);
        std::size_t from = 0;
        while (true) {
            std::size_t bar = right.find('|', from);
            std::string alt = right.substr(from, bar == std::string::npos ? std::string::npos
                                                                           : bar - from);
            for (char& c : alt) {
                if (c == '~') c = ' ';  // ~ в файле — это терминал «пробел»
                if (isNonterminal(c))
                    usedOnRight.push_back({c, lineNo});
                else if (std::find(g.terminals.begin(), g.terminals.end(), c) == g.terminals.end())
                    g.terminals.push_back(c);
            }
            auto& alts = g.rules[A];
            if (std::find(alts.begin(), alts.end(), alt) == alts.end()) alts.push_back(alt);
            if (bar == std::string::npos) break;
            from = bar + 1;
        }
    }

    if (g.start == 0) throw GrammarError("в файле нет ни одного правила");
    for (auto [B, ln] : usedOnRight)
        if (!g.rules.count(B))
            throw errorAt(ln, std::string("нетерминал ") + B +
                                  " встречается в правой части, но правил для него нет");
    return g;
}

// ---------------------------------------------------------------------------------------------
// Магазинный автомат
// ---------------------------------------------------------------------------------------------

class PushdownAutomaton {
public:
    explicit PushdownAutomaton(Grammar g);
    void printDefinition(std::ostream& out) const;
    bool recognize(std::string input, std::ostream& out);

private:
    // Конфигурация (s0, остаток входа, магазин) и номер команды, которой в неё пришли.
    // Состояние у автомата одно, поэтому храним только позицию во входе и магазин.
    struct Config {
        std::size_t pos;
        std::string stack;     // дно слева (H0), вершина — последний символ
        std::string cmd;
        std::size_t next = 0;  // сколько переходов из неё перебор уже испробовал
    };
    // Чем закончился шаг в новую конфигурацию.
    enum class Entry { Cut, Accept, Open };

    Grammar g_;
    std::map<char, std::size_t> minLen_;    // минимальная длина терминальной цепочки из A
    std::map<char, std::set<char>> first_;  // FIRST(A): с каких терминалов начинается вывод
    std::map<char, int> ntCmd_;             // номер команды типа (1) для нетерминала
    std::map<char, int> tCmd_;              // номер команды типа (2) для терминала
    int h0Cmd_ = 0;                         // номер команды типа (3)
    std::size_t maxRhs_ = 0;
    bool hasSpace_ = false;

    // Состояние текущего разбора.
    std::string input_;
    std::size_t stackLimit_ = 0;
    std::unordered_set<std::string> visited_;
    std::vector<Config> path_;      // текущая ветвь перебора
    std::vector<Config> bestPath_;  // ветвь, прочитавшая больше всего символов
    std::size_t bestSame_ = 0;      // столько первых конфигураций bestPath_ совпадают с path_
    std::size_t bestPos_ = 0;
    std::set<char> expected_;   // что могло стоять во входе на позиции bestPos_
    bool expectedEnd_ = false;  // ... или там мог быть конец цепочки
    bool aborted_ = false;
    std::size_t cutLength_ = 0, cutCount_ = 0, cutTail_ = 0, cutRepeat_ = 0, cutStack_ = 0;

    void computeMinLengths();
    void computeFirstSets();
    void noteDeadEnd(std::size_t pos, const std::string& stack);
    std::size_t minLength(const std::string& stack) const;
    bool tailMatches(std::size_t pos, const std::string& stack) const;
    bool terminalsFit(std::size_t pos, const std::string& stack) const;
    std::string configText(const Config& c) const;
    std::string ruleLabel(char A, std::size_t alt) const;
    void printPath(const std::vector<Config>& path, std::ostream& out) const;
    void printLeftDerivation(std::ostream& out) const;
    Entry enter(std::size_t pos, std::string stack, std::string cmd);
    void leave();
    bool search(const std::string& initial);
};

PushdownAutomaton::PushdownAutomaton(Grammar g) : g_(std::move(g)) {
    // Нумерация команд как в примере методички: сначала по одной команде (1) на каждый
    // нетерминал (альтернативы — подпункты k.1, k.2, ...), затем команды (2) для терминалов,
    // последней — команда (3) для дна магазина.
    int n = 0;
    for (char A : g_.nonterminals) ntCmd_[A] = ++n;
    for (char a : g_.terminals) tCmd_[a] = ++n;
    h0Cmd_ = ++n;

    for (const auto& [A, alts] : g_.rules)
        for (const auto& rhs : alts) maxRhs_ = std::max(maxRhs_, rhs.size());
    hasSpace_ = std::find(g_.terminals.begin(), g_.terminals.end(), ' ') != g_.terminals.end();
    computeMinLengths();
    computeFirstSets();
}

// minLen(A) — длина самой короткой терминальной цепочки, выводимой из A.
// Считаем итерациями до неподвижной точки: minLen(A) = min по правилам A -> X1..Xk
// суммы minLen(Xi), где у терминала длина 1. Для ε-правила сумма равна 0.
void PushdownAutomaton::computeMinLengths() {
    for (char A : g_.nonterminals) minLen_[A] = INF;
    bool changed = true;
    while (changed) {  // ЦИКЛ: пока хоть одно значение уменьшается
        changed = false;
        for (char A : g_.nonterminals) {
            for (const auto& rhs : g_.rules.at(A)) {
                std::size_t len = 0;
                for (char X : rhs) len = addSat(len, isNonterminal(X) ? minLen_[X] : 1);
                if (len < minLen_[A]) {
                    minLen_[A] = len;
                    changed = true;
                }
            }
        }
    }
}

// FIRST(A) — терминалы, с которых может начинаться цепочка, выводимая из A. Тоже неподвижная
// точка: для A -> X1 X2 ... добавляем FIRST(X1), а если X1 обнуляемый (minLen = 0), то
// и FIRST(X2), и так далее.
// Нужно только для сообщения «что ожидалось» при отказе, на сам разбор не влияет.
void PushdownAutomaton::computeFirstSets() {
    bool changed = true;
    while (changed) {
        changed = false;
        for (char A : g_.nonterminals) {
            auto& f = first_[A];
            std::size_t before = f.size();
            for (const auto& rhs : g_.rules.at(A)) {
                for (char X : rhs) {
                    if (!isNonterminal(X)) {
                        f.insert(X);
                        break;
                    }
                    f.insert(first_[X].begin(), first_[X].end());
                    if (minLen_.at(X) != 0) break;
                }
            }
            if (f.size() != before) changed = true;
        }
    }
}

// Ветвь зашла в тупик на позиции bestPos_ — запоминаем, какой символ она была готова прочитать
// следующим: FIRST от содержимого магазина сверху вниз (или конец цепочки, если всё обнуляемо).
void PushdownAutomaton::noteDeadEnd(std::size_t pos, const std::string& stack) {
    if (pos != bestPos_) return;
    for (auto it = stack.rbegin(); it != stack.rend(); ++it) {
        char X = *it;
        if (X == H0) break;
        if (!isNonterminal(X)) {
            expected_.insert(X);
            return;
        }
        expected_.insert(first_.at(X).begin(), first_.at(X).end());
        if (minLen_.at(X) != 0) return;
    }
    expectedEnd_ = true;
}

// Сколько входных символов как минимум «съест» содержимое магазина.
std::size_t PushdownAutomaton::minLength(const std::string& stack) const {
    std::size_t total = 0;
    for (char X : stack) {
        if (X == H0) continue;
        total = addSat(total, isNonterminal(X) ? minLen_.at(X) : 1);
    }
    return total;
}

// Терминалы, лежащие подряд у самого дна, автомат прочитает последними, и снять их можно
// только командой (2). Значит, они обязаны совпасть с концом входной цепочки:
// stack[1] — с последним символом входа, stack[2] — с предпоследним и т.д.
bool PushdownAutomaton::tailMatches(std::size_t pos, const std::string& stack) const {
    std::size_t end = input_.size();
    for (std::size_t i = 1; i < stack.size() && !isNonterminal(stack[i]); ++i) {
        if (end == pos || input_[end - 1] != stack[i]) return false;
        --end;
    }
    return true;
}

// Каждый терминал из магазина когда-нибудь будет снят командой (2), то есть прочитан.
// Поэтому любого терминала в магазине не может быть больше, чем его осталось во входе.
// При левой рекурсии E -> E+T каждый виток кладёт в магазин '+', и рекурсия обрывается,
// как только плюсов в магазине становится больше, чем во входе.
bool PushdownAutomaton::terminalsFit(std::size_t pos, const std::string& stack) const {
    int balance[256] = {};
    for (std::size_t i = pos; i < input_.size(); ++i)
        ++balance[static_cast<unsigned char>(input_[i])];
    for (char X : stack) {
        if (X == H0 || isNonterminal(X)) continue;
        if (--balance[static_cast<unsigned char>(X)] < 0) return false;
    }
    return true;
}

std::string PushdownAutomaton::ruleLabel(char A, std::size_t alt) const {
    std::string label = "(" + std::to_string(ntCmd_.at(A));
    if (g_.rules.at(A).size() > 1) label += "." + std::to_string(alt + 1);
    return label + ")";
}

void PushdownAutomaton::printDefinition(std::ostream& out) const {
    auto list = [](const std::vector<std::string>& items) {
        std::string s = "{";
        for (std::size_t i = 0; i < items.size(); ++i) s += (i ? ", " : "") + items[i];
        return s + "}";
    };
    std::vector<std::string> vn, vt;
    for (char A : g_.nonterminals) vn.push_back(show(A));
    for (char a : g_.terminals) vt.push_back(show(a));

    out << "Грамматика G = {VN, VT, I, P}:\n";
    out << "  VN = " << list(vn) << "\n  VT = " << list(vt) << "\n  I  = " << g_.start << "\n";
    out << "  Правила:\n";
    for (char A : g_.nonterminals) {
        out << "    " << A << " -> ";
        const auto& alts = g_.rules.at(A);
        for (std::size_t i = 0; i < alts.size(); ++i) out << (i ? " | " : "") << show(alts[i]);
        out << "\n";
    }

    std::vector<std::string> z = vn;
    z.insert(z.end(), vt.begin(), vt.end());
    z.push_back("h0");
    out << "\nМагазинный автомат M = {S, P, Z, δ, s0, h0, F}:\n";
    out << "  S = {s0}\n  P = " << list(vt) << "\n  Z = " << list(z) << "\n";
    out << "  s0 — начальное состояние, h0 — маркер дна магазина\n  F = {s0}\n";

    out << "\nКоманды типа (1) — замена нетерминала в вершине правой частью правила (в реверсе):\n";
    for (char A : g_.nonterminals) {
        const auto& alts = g_.rules.at(A);
        out << "  (" << ntCmd_.at(A) << ") δ0(s0, ε, " << A << ") = ";
        if (alts.size() > 1) out << "{";
        for (std::size_t i = 0; i < alts.size(); ++i) {
            std::string rev(alts[i].rbegin(), alts[i].rend());
            out << (i ? "; " : "") << "(s0, " << show(rev) << ")";
        }
        if (alts.size() > 1) out << "}";
        out << "\n";
    }
    out << "Команды типа (2) — совпадение терминала на входе и в вершине:\n";
    for (char a : g_.terminals)
        out << "  (" << tCmd_.at(a) << ") δ(s0, " << show(a) << ", " << show(a) << ") = (s0, ε)\n";
    out << "Команда типа (3) — переход в заключительную конфигурацию:\n";
    out << "  (" << h0Cmd_ << ") δ(s0, ε, h0) = (s0, ε)\n";
    out << "Тип (4) — начальная конфигурация: (s0, α, h0" << g_.start
        << "), α — исходная цепочка\n";

    out << "\nМинимальная длина выводимой цепочки (для отсечения перебора):";
    for (char A : g_.nonterminals)
        out << "  " << A << ": " << (minLen_.at(A) == INF ? "∞" : std::to_string(minLen_.at(A)));
    out << "\n";
    for (char A : g_.nonterminals)
        if (minLen_.at(A) == INF)
            out << "Предупреждение: из " << A << " не выводится ни одна терминальная цепочка.\n";
}

std::string PushdownAutomaton::configText(const Config& c) const {
    return "(s0, " + show(input_.substr(c.pos)) + ", " + show(c.stack) + ")";
}

void PushdownAutomaton::printPath(const std::vector<Config>& path, std::ostream& out) const {
    std::size_t width = 0;
    for (const auto& c : path) width = std::max(width, screenWidth(configText(c)));
    for (std::size_t i = 0; i < path.size(); ++i) {
        std::string text = configText(path[i]);
        out << (i ? "├ " : "  ") << text;
        if (!path[i].cmd.empty())
            out << std::string(width - screenWidth(text) + 3, ' ') << path[i].cmd;
        out << "\n";
    }
}

// Левый вывод восстанавливается по успешной ветви: после каждой команды (1) сентенциальная
// форма = уже прочитанная часть входа + содержимое магазина сверху вниз (без h0).
void PushdownAutomaton::printLeftDerivation(std::ostream& out) const {
    std::string line = std::string(1, g_.start);
    for (std::size_t i = 1; i < path_.size(); ++i) {
        const Config& prev = path_[i - 1];
        if (prev.stack.empty() || !isNonterminal(prev.stack.back())) continue;
        const Config& c = path_[i];
        std::string form = input_.substr(0, c.pos);
        for (auto it = c.stack.rbegin(); it != c.stack.rend(); ++it)
            if (*it != H0) form += *it;
        line += " ⇒ " + show(form);
    }
    out << "Левый вывод: " << line << "\n";
}

// Возврат: снимаем последнюю конфигурацию с ветви. Совпадать с bestPath_ теперь может
// только то, что на ветви осталось.
void PushdownAutomaton::leave() {
    path_.pop_back();
    bestSame_ = std::min(bestSame_, path_.size());
}

// Шаг в конфигурацию (s0, input_[pos..], stack). Если она отсечена или из неё нет ни одного
// перехода — Cut, если она заключительная — Accept, иначе она остаётся на ветви (Open).
PushdownAutomaton::Entry PushdownAutomaton::enter(std::size_t pos, std::string stack,
                                                  std::string cmd) {
    if (visited_.size() >= MAX_VISITED) {
        aborted_ = true;
        return Entry::Cut;
    }
    // Отсечение 1: в этой конфигурации уже были — всё, что из неё достижимо, уже проверено
    // (или проверяется прямо сейчас выше по ветви, и тогда это цикл).
    if (!visited_.insert(std::to_string(pos) + ":" + stack).second) {
        ++cutRepeat_;
        return Entry::Cut;
    }

    path_.push_back({pos, std::move(stack), std::move(cmd)});
    const std::string& st = path_.back().stack;
    if (pos > bestPos_ || bestPath_.empty()) {  // РАЗВИЛКА: новый рекорд по прочитанному
        bestPos_ = pos;
        // Дописываем только то, чем ветвь отличается от прошлой лучшей: копировать весь путь
        // на каждом прочитанном символе длинной цепочки слишком дорого.
        bestPath_.resize(bestSame_);
        bestPath_.insert(bestPath_.end(), path_.begin() + bestSame_, path_.end());
        bestSame_ = path_.size();
        expected_.clear();
        expectedEnd_ = false;
    }

    const std::size_t rest = input_.size() - pos;
    bool open = false;
    if (minLength(st) > rest) {
        // Отсечение 2: магазин заведомо породит больше символов, чем осталось на входе.
        // Именно оно обрывает левую рекурсию E -> E+T: каждый виток добавляет +T.
        ++cutLength_;
    } else if (!terminalsFit(pos, st)) {
        // Отсечение 3: какого-то терминала в магазине больше, чем осталось во входе.
        ++cutCount_;
    } else if (!tailMatches(pos, st)) {
        // Отсечение 4: терминалы у дна не совпадают с концом входа. Без него левая рекурсия
        // S -> Sa | Sb перебирает все 2^n вариантов «хвоста» до того, как прочитать хоть символ.
        ++cutTail_;
    } else if (st.size() > stackLimit_) {
        // Отсечение 5: нужно только для грамматик с ε-правилами (см. README).
        ++cutStack_;
    } else if (st.empty()) {
        // Дно уже снято командой (3): допускаем, только если вход прочитан полностью.
        if (rest == 0) return Entry::Accept;
    } else if (isNonterminal(st.back()) || st.back() == H0) {
        open = true;  // применима команда (1) или (3)
    } else {
        open = rest > 0 && input_[pos] == st.back();  // применима ли команда (2)
    }
    if (open) return Entry::Open;
    noteDeadEnd(pos, st);  // для диагностики: что эта ветвь ждала дальше
    leave();
    return Entry::Cut;
}

// Перебор в глубину с возвратом. Рекурсии нет: ветвь лежит в path_, и у каждой конфигурации
// в поле next записано, сколько переходов из неё уже испробовано, — так цепочка в тысячи
// символов не переполняет стек вызовов. Возвращает true, если дошли до (s0, ε, ε);
// тогда path_ — вся успешная цепочка конфигураций.
bool PushdownAutomaton::search(const std::string& initial) {
    if (enter(0, initial, "") == Entry::Accept) return true;
    while (!path_.empty() && !aborted_) {  // ЦИКЛ: пока на ветви есть что продолжать
        Config& c = path_.back();
        const char top = c.stack.back();
        const std::string below = c.stack.substr(0, c.stack.size() - 1);
        const std::size_t pos = c.pos, i = c.next++;
        Entry e;
        if (isNonterminal(top)) {  // РАЗВИЛКА: команда (1), альтернативы по порядку
            const auto& alts = g_.rules.at(top);
            if (i == alts.size()) {  // все альтернативы испробованы — возврат
                leave();
                continue;
            }
            std::string next = below + std::string(alts[i].rbegin(), alts[i].rend());  // αᴿ
            e = enter(pos, std::move(next), ruleLabel(top, i));
        } else if (i > 0) {  // у команд (2) и (3) переход один, и он уже испробован — возврат
            leave();
            continue;
        } else if (top == H0) {
            e = enter(pos, below, "(" + std::to_string(h0Cmd_) + ")");  // команда (3)
        } else {
            e = enter(pos + 1, below, "(" + std::to_string(tCmd_.at(top)) + ")");  // команда (2)
        }
        if (e == Entry::Accept) return true;
    }
    return false;
}

bool PushdownAutomaton::recognize(std::string input, std::ostream& out) {
    // Пробел — терминал только если он есть в грамматике (записан как ~). Тогда ~ во вводе
    // означает пробел. Иначе пробелы во вводе незначащие, как в примере методички «a + a*a».
    std::string clean;
    bool dropped = false;
    for (char c : input) {
        if (hasSpace_ && c == '~') c = ' ';
        if (!hasSpace_ && (c == ' ' || c == '\t')) {
            dropped = true;
            continue;
        }
        clean += c;
    }
    input_ = clean;

    // Сброс состояния поиска.
    // Граница высоты магазина: в кратчайшем дереве вывода на пути от корня вниз подряд идущие
    // узлы с одинаковой длиной кроны не повторяют нетерминал, поэтому глубина дерева не больше
    // (n+1)*|VN|, а каждый узел на пути держит в магазине не больше (maxRhs-1) символов.
    stackLimit_ = 2 + (input_.size() + 1) * g_.nonterminals.size() *
                          std::max<std::size_t>(1, maxRhs_ ? maxRhs_ - 1 : 0);
    visited_.clear();
    path_.clear();
    bestPath_.clear();
    bestSame_ = 0;
    bestPos_ = 0;
    expected_.clear();
    expectedEnd_ = aborted_ = false;
    cutLength_ = cutCount_ = cutTail_ = cutRepeat_ = cutStack_ = 0;

    out << "\nЦепочка: " << show(input_) << " (длина " << screenWidth(input_) << ")\n";
    if (dropped) out << "Пробелы во вводе отброшены: в грамматике нет терминала-пробела.\n";

    // Терминалы грамматики — только печатные ASCII-символы. Символ вне них (например, буква
    // кириллицы) не прочтёт ни одна команда (2), так что по байтам UTF-8 его не разбираем.
    auto bad = std::find_if(input_.begin(), input_.end(), [](char c) {
        auto u = static_cast<unsigned char>(c);
        return u < 0x20 || u >= 0x7F;
    });
    if (bad != input_.end()) {
        auto stop = std::find_if(bad + 1, input_.end(), [](char c) {
            return (static_cast<unsigned char>(c) & 0xC0) != 0x80;  // конец символа UTF-8
        });
        out << "Символ «" << std::string(bad, stop) << "» не входит во входной алфавит P: "
               "его не прочтёт ни одна команда (2).\n";
        out << "Заключение: цепочка " << show(input_) << " НЕ ДОПУСКАЕТСЯ автоматом.\n";
        return false;
    }

    bool ok = search(std::string(1, H0) + g_.start);

    out << "Просмотрено конфигураций: " << visited_.size() << "; отсечено: по длине "
        << cutLength_ << ", по составу " << cutCount_ << ", по хвосту " << cutTail_
        << ", повторов " << cutRepeat_ << ", по высоте магазина " << cutStack_ << "\n";

    if (ok) {
        out << "Цепочка конфигураций (" << tacts(path_.size() - 1) << "):\n";
        printPath(path_, out);
        printLeftDerivation(out);
        out << "Заключение: цепочка " << show(input_) << " ДОПУСКАЕТСЯ автоматом.\n";
        return true;
    }

    if (aborted_) {
        out << "Поиск прерван: превышен предел в " << MAX_VISITED << " конфигураций.\n";
        out << "Заключение: допустимость цепочки " << show(input_) << " не установлена.\n";
        return false;
    }

    out << "Ни одна ветвь не дошла до заключительной конфигурации (s0, ε, ε).\n";
    out << "Дальше всех продвинулась ветвь (прочитано символов: " << bestPos_ << " из "
        << input_.size() << "):\n";
    printPath(bestPath_, out);
    std::string seen = bestPos_ < input_.size() ? "«" + show(input_[bestPos_]) + "»"
                                                : "конец цепочки";
    if (!expected_.empty() || expectedEnd_) {
        out << "Ветви, дошедшие до позиции " << bestPos_ + 1 << ", ждали там: ";
        bool first = true;
        for (char a : expected_) {
            out << (first ? "" : ", ") << show(a);
            first = false;
        }
        if (expectedEnd_) out << (first ? "" : ", ") << "конец цепочки";
        out << "; на входе " << seen << ".\n";
        // Символ мог и подойти: тогда ветвь погибла не на нём, а из-за отсечения по остатку.
        if (bestPos_ < input_.size() && expected_.count(input_[bestPos_]))
            out << "Символ " << seen << " подходит, но остаток входа не согласуется с магазином "
                   "(не хватает длины, нужных терминалов или не тот конец цепочки).\n";
    }
    if (minLen_.at(g_.start) == INF)
        out << "Из " << g_.start << " не выводится ни одна терминальная цепочка.\n";
    else if (minLen_.at(g_.start) > input_.size())
        out << "Из " << g_.start << " выводятся цепочки длиной не меньше " << minLen_.at(g_.start)
            << ", а во входе " << input_.size() << " симв., поэтому разбор даже не начат.\n";
    out << "Заключение: цепочка " << show(input_) << " НЕ ДОПУСКАЕТСЯ автоматом.\n";
    return false;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Использование: " << argv[0] << " <файл грамматики>\n";
        return 1;
    }

    Grammar g;
    try {
        g = readGrammar(argv[1]);
    } catch (const GrammarError& e) {
        std::cerr << "Ошибка в грамматике: " << e.what() << "\n";
        return 1;
    }

    PushdownAutomaton automaton(std::move(g));
    automaton.printDefinition(std::cout);

    // Цепочки читаем до пустой строки или конца ввода. Пустую цепочку вводим как ε.
    const bool interactive = isatty(STDIN_FILENO);
    std::string line;
    while (true) {  // ЦИКЛ ввода цепочек
        if (interactive) std::cout << "\nВведите цепочку (пустая строка — выход): " << std::flush;
        if (!std::getline(std::cin, line)) break;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) break;
        if (line == "ε") line.clear();
        automaton.recognize(line, std::cout);
    }
    return 0;
}
