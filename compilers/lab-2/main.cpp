// ЛР2 ТАЯК. Конечный автомат: чтение из файла, анализ, детерминизация,
// разбор строк. Запуск: ./lab2 <файл автомата> [строка ...] [--dot] [--dfa-out файл]
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <unistd.h>  // isatty — печатать ли приглашение "> "

#include "automaton.h"

namespace {

void usage() {
    std::cout << "Использование: ./lab2 <файл автомата> [строка ...] [--dot] [--dfa-out <файл>]\n"
                 "  строки после имени файла проверяются сразу; если их нет —\n"
                 "  вводятся с клавиатуры по одной, пустая строка или Ctrl+D — выход.\n"
                 "  --dot              записать графы <файл>.dot и <файл>.dfa.dot (Graphviz)\n"
                 "  --dfa-out <файл>   сохранить правила ДКА в формате входного файла\n";
}

std::string joinStates(const StateSet& set) {
    std::string out;
    for (const State& s : set) out += (out.empty() ? "" : " ") + s.name();
    return out.empty() ? "нет" : out;
}

// Общие сведения: состояния, алфавит, таблица переходов.
void describe(const FiniteAutomaton& fa) {
    StateSet st = fa.states(), fin = fa.finals();
    std::set<Symbol> alpha = fa.alphabet();
    std::cout << "Состояний: " << st.size() << ": " << joinStates(st) << '\n'
              << "Начальное: q0\n"
              << "Конечных: " << fin.size() << ": " << joinStates(fin) << '\n'
              << "Алфавит (" << alpha.size() << "):";
    for (const Symbol& s : alpha) std::cout << ' ' << showSym(s);
    std::cout << "\nПравил: " << fa.rules().size() << "\n\n";

    if (alpha.size() <= 24) {
        std::cout << "Таблица переходов (-> начальное, * конечное, - перехода нет):\n";
        fa.printTable(std::cout);
    } else {
        std::cout << "Таблица переходов не выводится: в алфавите " << alpha.size() << " символов.\n";
    }
}

// Висячие вершины: недостижимые из q0 и тупиковые (конечное недостижимо).
void reportHanging(const FiniteAutomaton& fa) {
    StateSet unreach = fa.unreachable(), dead = fa.dead();

    if (unreach.empty())
        std::cout << "Недостижимых состояний нет: в каждое можно попасть из q0.\n";
    else
        std::cout << "Недостижимые из q0 состояния: " << joinStates(unreach)
                  << " — их правила никогда не сработают.\n";

    if (dead.empty()) {
        std::cout << "Тупиковых состояний нет: из каждого можно дойти до конечного.\n";
        return;
    }
    std::cout << "Тупиковые состояния (из них не дойти ни до одного конечного):\n";
    for (const State& s : dead) {
        std::cout << "  " << s.name() << " — "
                  << (fa.hasOutgoing(s) ? "переходы есть, но все ведут в тупик или по кругу"
                                        : "из него нет ни одного перехода")
                  << (unreach.contains(s) ? " (к тому же недостижимо)" : "") << '\n';
    }
    if (dead.contains(FiniteAutomaton::kStart))
        std::cout << "  Тупик — само q0, поэтому автомат не допускает ни одной строки.\n";
}

// Проверка одной строки и вывод заключения.
void checkString(const std::string& str, const FiniteAutomaton& dfa,
                 const FiniteAutomaton& original, bool wasNfa) {
    RunResult r = dfa.run(str);
    std::cout << '"' << str << "\" — " << (r.accepted ? "ДОПУСКАЕТСЯ" : "НЕ ДОПУСКАЕТСЯ");
    if (!r.accepted) std::cout << ": " << r.reason;
    std::cout << '\n';

    // Путь по автомату: q0 -'a'-> q2 -'b'-> q3 ...
    std::cout << "    путь" << (wasNfa ? " по ДКА" : "") << ": " << r.path[0].name();
    for (size_t i = 1; i < r.path.size(); ++i)
        std::cout << " -" << showSym(r.input[i - 1]) << "-> " << r.path[i].name();
    std::cout << '\n';

    if (wasNfa) {  // сверка: прямое моделирование НКА должно дать тот же ответ
        if (original.runNfa(str) == r.accepted)
            std::cout << "    (моделирование исходного НКА даёт тот же ответ)\n";
        else
            std::cout << "    ВНИМАНИЕ: НКА и ДКА разошлись — ошибка в детерминизации!\n";
    }
}

}  // namespace

int main(int argc, char* argv[]) {
    // ---- разбор аргументов ----
    std::string file, dfaOut;
    std::vector<std::string> strings;
    bool dot = false, haveStrings = false;
    for (int i = 1; i < argc; ++i) {  // ЦИКЛ: по аргументам командной строки
        std::string a = argv[i];
        if (a == "-h" || a == "--help") { usage(); return 0; }
        if (a == "--dot") dot = true;
        else if (a == "--dfa-out") {
            if (i + 1 == argc) { std::cerr << "Ошибка: после --dfa-out нужно имя файла\n"; return 2; }
            dfaOut = argv[++i];
        }
        else if (file.empty()) file = a;
        else { strings.push_back(a); haveStrings = true; }
    }
    if (file.empty()) { usage(); return 2; }

    // ---- чтение файла ----
    std::cout << "=== Файл " << file << " ===\n";
    RuleFileReader reader = [&] {
        try {
            return RuleFileReader(file);
        } catch (const std::exception& e) {
            std::cerr << "Ошибка: " << e.what() << '\n';
            std::exit(1);
        }
    }();
    std::cout << "Строк в файле: " << reader.totalLines() << ", правил: " << reader.rules().size()
              << ", пустых и комментариев: " << reader.skippedLines()
              << ", с ошибками: " << reader.errors().size() << '\n';

    if (!reader.errors().empty()) {
        std::cout << "\n=== Синтаксические ошибки (эти строки пропущены) ===\n";
        for (const SyntaxError& e : reader.errors())
            std::cout << "  строка " << e.line << ": \"" << e.text << "\" — " << e.message << '\n';
    }
    if (reader.rules().empty()) {
        std::cout << "\nВ файле нет ни одного правильного правила — строить нечего.\n";
        return 1;
    }

    FiniteAutomaton fa(reader.rules());
    if (!fa.duplicates().empty()) std::cout << "\n=== Повторяющиеся правила (учтены один раз) ===\n";
    for (const Rule& d : fa.duplicates())
        std::cout << "  строка " << d.line << ": правило " << d.from.name() << ',' << d.sym << '='
                  << d.to.name() << " уже было выше\n";

    // ---- информация об автомате ----
    std::cout << "\n=== Автомат ===\n";
    describe(fa);
    if (!fa.hasTransitionsFromStart())
        std::cout << "\nВнимание: из начального состояния q0 нет переходов.\n";
    if (fa.finals().empty())
        std::cout << "\nВнимание: конечных состояний (f<N>) нет — ни одна строка не будет допущена.\n";

    std::cout << "\n=== Детерминированность ===\n";
    std::vector<Conflict> conf = fa.conflicts();
    bool nfa = !conf.empty();
    if (!nfa) {
        std::cout << "Автомат ДЕТЕРМИНИРОВАН: из каждого состояния по каждому символу не больше одного перехода.\n";
    } else {
        std::cout << "Автомат НЕДЕТЕРМИНИРОВАН: по одному символу из одного состояния есть переходы\n"
                     "в разные состояния (" << conf.size() << " случ.):\n";
        for (const Conflict& c : conf) {  // ЦИКЛ: по конфликтующим парам (состояние, символ)
            StateSet to;
            std::string lines;
            for (const Rule& r : c.rules) {
                to.insert(r.to);
                lines += (lines.empty() ? "" : ", ") + std::to_string(r.line);
            }
            std::cout << "  " << c.from.name() << " по " << showSym(c.sym) << " -> " << showSet(to)
                      << "   (строки " << lines << ")\n";
        }
    }

    std::cout << "\n=== Висячие вершины ===\n";
    reportHanging(fa);

    // ---- детерминизация ----
    Determinized det = fa.determinize();
    if (nfa) {
        std::cout << "\n=== Детерминизация (построение подмножеств) ===\n"
                     "Состояния ДКА (в порядке появления) и из чего они состоят:\n";
        for (const auto& [st, set] : det.composition) {
            std::cout << "  " << st.name() << " = " << showSet(set);
            if (set.size() > 1 && st.final) std::cout << "   конечное: содержит конечное состояние";
            else if (set.size() > 1) std::cout << "   новое";
            std::cout << '\n';
        }
        std::cout << "\nПереходы ДКА в формате входного файла:\n";
        det.dfa.printRules(std::cout);
        std::cout << '\n';
        describe(det.dfa);
        StateSet deadDfa = det.dfa.dead();
        if (!deadDfa.empty())
            std::cout << "Тупиковые состояния ДКА: " << joinStates(deadDfa) << '\n';
    }

    // ---- выгрузка в файлы ----
    if (!dfaOut.empty()) {
        std::ofstream out(dfaOut);
        (nfa ? det.dfa : fa).printRules(out);
        if (out) std::cout << "\nПравила " << (nfa ? "ДКА" : "автомата") << " сохранены в " << dfaOut << '\n';
        else std::cerr << "Ошибка: не удалось записать " << dfaOut << '\n';
    }
    if (dot) {
        size_t slash = file.find_last_of('/');
        std::string title = file.substr(slash == std::string::npos ? 0 : slash + 1);  // имя без каталога
        // Расширение срезаем только у имени файла: точки в "../" или "./" не трогаем.
        std::string base = file;
        size_t dotPos = title.rfind('.');
        if (dotPos != std::string::npos && dotPos > 0) base.resize(file.size() - (title.size() - dotPos));
        {
            std::ofstream out(base + ".dot");
            fa.writeDot(out, title + (nfa ? " (НКА)" : ""));
        }
        std::cout << "\nГраф записан в " << base << ".dot";
        if (nfa) {
            std::map<State, StateSet> comp(det.composition.begin(), det.composition.end());
            std::ofstream out(base + ".dfa.dot");
            det.dfa.writeDot(out, title + " (ДКА)", comp);
            std::cout << " и " << base << ".dfa.dot";
        }
        std::cout << "\nКартинка: nix shell nixpkgs#graphviz -c dot -Tpng " << base
                  << ".dot -o graph.png  (или вставить текст на graphviz.online)\n";
    }

    // ---- разбор строк ----
    const FiniteAutomaton& worker = nfa ? det.dfa : fa;
    std::cout << "\n=== Проверка строк" << (nfa ? " (через ДКА)" : "") << " ===\n";
    if (haveStrings) {
        for (const std::string& s : strings) checkString(s, worker, fa, nfa);
        return 0;
    }

    bool tty = isatty(0);
    if (tty) std::cout << "Вводите строки по одной; пустая строка или Ctrl+D — выход.\n";
    std::string line;
    while (true) {  // ЦИКЛ: пока пользователь вводит строки
        if (tty) std::cout << "> " << std::flush;
        if (!std::getline(std::cin, line)) break;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) break;
        checkString(line, worker, fa, nfa);
    }
    return 0;
}
