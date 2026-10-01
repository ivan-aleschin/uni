// ЛР2 ТАЯК: конечный автомат, чтение из файла, анализ и детерминизация.
// Здесь только объявления; реализация — в automaton.cpp.
#pragma once

#include <compare>
#include <map>
#include <ostream>
#include <set>
#include <string>
#include <utility>
#include <vector>

// Состояние автомата: q<N> — обычное, f<N> — конечное (допускающее).
// q0 и f0 — два разных состояния, поэтому храним пару (конечное?, номер).
struct State {
    bool final = false;
    long long num = 0;

    std::string name() const { return (final ? "f" : "q") + std::to_string(num); }
    // Сортировка: сначала все q по номеру, потом все f по номеру.
    auto operator<=>(const State&) const = default;
};

using StateSet = std::set<State>;
// Символ перехода — один символ строки. Храним как std::string, чтобы
// русская буква в UTF-8 (2 байта) тоже считалась одним символом.
using Symbol = std::string;

// Одно правило вида q<N>,<C>=<q|f><N> и номер строки файла, где оно записано.
struct Rule {
    State from;
    Symbol sym;
    State to;
    int line = 0;  // 0 — правило построено программой (у ДКА)
};

// Синтаксическая ошибка в файле: номер строки, сама строка и что не так.
struct SyntaxError {
    int line;
    std::string text;
    std::string message;
};

// Конфликт недетерминированности: из одного состояния по одному символу
// есть правила в разные состояния.
struct Conflict {
    State from;
    Symbol sym;
    std::vector<Rule> rules;
};

// Результат разбора строки детерминированным автоматом.
struct RunResult {
    bool accepted = false;
    std::vector<State> path;   // пройденные состояния, начиная с q0
    std::vector<Symbol> input; // строка, разбитая на символы
    std::string reason;        // почему отвергнута (пусто, если допущена)
};

// Вспомогательные функции для символов и множеств.
std::vector<Symbol> splitSymbols(const std::string& s);  // строка -> символы (UTF-8)
std::string showSym(const Symbol& s);                    // 'a', ' ', '\t' — в кавычках
std::string showSet(const StateSet& set);                // {q1, q3, f0}

// Чтение файла с правилами. Ошибочные строки не останавливают чтение:
// они попадают в errors(), а правильные строки — в rules().
class RuleFileReader {
public:
    explicit RuleFileReader(const std::string& path);  // runtime_error, если файл не открыть

    const std::vector<Rule>& rules() const { return rules_; }
    const std::vector<SyntaxError>& errors() const { return errors_; }
    int totalLines() const { return totalLines_; }
    int skippedLines() const { return skippedLines_; }  // пустые и комментарии

    // Разбор одной строки. true — правило в rule, false — текст ошибки в err.
    static bool parseLine(const std::string& line, Rule& rule, std::string& err);

private:
    std::vector<Rule> rules_;
    std::vector<SyntaxError> errors_;
    int totalLines_ = 0;
    int skippedLines_ = 0;
};

struct Determinized;

// Конечный автомат (в общем случае недетерминированный).
// Функция переходов хранится как delta_[состояние][символ] = множество состояний.
class FiniteAutomaton {
public:
    static constexpr State kStart{false, 0};  // начальное состояние всегда q0

    FiniteAutomaton() = default;
    explicit FiniteAutomaton(const std::vector<Rule>& rules);

    // Добавить правило. false — точно такое же правило уже было (дубликат).
    bool addRule(const Rule& r);

    const std::vector<Rule>& rules() const { return rules_; }
    const std::vector<Rule>& duplicates() const { return duplicates_; }

    StateSet states() const;
    StateSet finals() const;
    std::set<Symbol> alphabet() const;
    bool hasTransitionsFromStart() const { return delta_.contains(kStart); }

    // Куда можно перейти из state по символу sym (пусто — перехода нет).
    StateSet targets(const State& state, const Symbol& sym) const;
    // Символы, по которым из state вообще есть переходы.
    std::vector<Symbol> expectedSymbols(const State& state) const;

    // Анализ автомата.
    std::vector<Conflict> conflicts() const;  // пусто <=> автомат детерминирован
    bool isDeterministic() const { return conflicts().empty(); }
    StateSet unreachable() const;  // недостижимы из q0
    StateSet dead() const;         // из них нельзя попасть ни в одно конечное
    bool hasOutgoing(const State& s) const { return delta_.contains(s); }

    // Построение подмножеств: эквивалентный детерминированный автомат.
    Determinized determinize() const;

    // Разбор строки. run() — только для детерминированного автомата,
    // runNfa() — прямое моделирование НКА множеством текущих состояний.
    RunResult run(const std::string& input) const;
    bool runNfa(const std::string& input) const;

    // Вывод: правила в формате входного файла, таблица переходов, граф Graphviz.
    void printRules(std::ostream& out) const;
    void printTable(std::ostream& out) const;
    void writeDot(std::ostream& out, const std::string& title,
                  const std::map<State, StateSet>& composition = {}) const;

private:
    std::vector<Rule> rules_;       // уникальные правила в порядке добавления
    std::vector<Rule> duplicates_;  // повторы, которые были отброшены
    std::map<State, std::map<Symbol, StateSet>> delta_;
    StateSet allStates_;
};

// Результат детерминизации: сам ДКА и из каких старых состояний состоит
// каждое его состояние (в порядке появления при обходе).
struct Determinized {
    FiniteAutomaton dfa;
    std::vector<std::pair<State, StateSet>> composition;
};
