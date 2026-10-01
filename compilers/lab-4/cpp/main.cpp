// ЛР4 по ТАЯК: синтаксический анализатор C-light, обнаруживающий наибольшее
// число ошибок. Лексер → FIRST/FOLLOW → таблица M[A, a] → нерекурсивный
// предиктивный анализатор со стеком и восстановлением после ошибок.
//
// Запуск:  ./lab4 [--phrase] [--ext] [--out DIR] файл.cl
//          ./lab4 --table [--ext] [--out DIR]
//   --phrase  восстановление в режиме фразы (по умолчанию — режим паники)
//   --ext     расширенная грамматика: в { } последовательность операторов
//   --out     куда писать таблицы (по умолчанию results/ рядом с бинарём, т. е. cpp/results)
//   --table   только построить таблицу предиктивного анализа
//
// Файлы:  DIR/<имя>.trace.md         — ход разбора (как пример 4), режим паники
//         DIR/<имя>.phrase.trace.md  — то же в режиме фразы
//         DIR/parse_table.md (parse_table_ext.md) — FIRST, FOLLOW, synch, M[A, a]
// Код возврата: 0 — ошибок нет, 1 — найдены ошибки, 2 — неверный запуск.

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "grammar.hpp"
#include "lexer.hpp"
#include "parser.hpp"

namespace fs = std::filesystem;

// Ширина строки в символах (а не в байтах) — для выравнивания столбцов с кириллицей.
static size_t width(const std::string& s) {
    size_t n = 0;
    for (unsigned char c : s) n += (c & 0xC0) != 0x80;
    return n;
}

static std::string pad(const std::string& s, size_t w) { return s + std::string(w > width(s) ? w - width(s) : 0, ' '); }

// Markdown-таблица с выровненными столбцами: читается и на GitHub, и в обычном редакторе.
static void writeTable(std::ostream& out, const std::vector<std::string>& head,
                       const std::vector<std::vector<std::string>>& rows) {
    std::vector<size_t> w(head.size(), 3);
    for (size_t j = 0; j < head.size(); ++j) w[j] = std::max(w[j], width(head[j]));
    for (const auto& r : rows)
        for (size_t j = 0; j < r.size(); ++j) w[j] = std::max(w[j], width(r[j]));
    auto line = [&](const std::vector<std::string>& r) {
        out << "|";
        for (size_t j = 0; j < r.size(); ++j) out << " " << pad(r[j], w[j]) << " |";
        out << "\n";
    };
    line(head);
    out << "|";
    for (size_t j = 0; j < head.size(); ++j) out << std::string(w[j] + 2, '-') << "|";
    out << "\n";
    for (const auto& r : rows) line(r);
}

static std::string joinSet(const std::set<std::string>& s, const std::vector<std::string>& order) {
    // Выводим в порядке столбцов таблицы, ε — в конце.
    std::string r;
    for (const auto& t : order)
        if (s.count(t)) r += (r.empty() ? "" : " ") + t;
    if (s.count(EPS)) r += (r.empty() ? "" : " ") + EPS;
    return r;
}

// Файл с грамматикой, FIRST/FOLLOW/synch и таблицей M[A, a].
static void writeParseTable(const Grammar& g, const fs::path& file) {
    std::ofstream out(file);
    out << "# Таблица предиктивного анализа C-light" << (g.ext ? " (расширенная грамматика, --ext)" : "")
        << "\n\nСгенерировано программой ЛР4 (`lab4`) по грамматике\n"
        << "из `grammar.hpp`.\n"
        << "Нетерминалы — в угловых скобках, `id` и `num` — токены лексера (`<identifier>` и `<number>`).\n\n";

    out << "## Продукции\n\n```\n";
    for (size_t k = 0; k < g.prods.size(); ++k) out << (k + 1 < 10 ? " " : "") << k + 1 << ". " << g.productionText(k) << "\n";
    out << "```\n\n";

    out << "## FIRST, FOLLOW и синхронизирующие множества\n\n";
    std::vector<std::vector<std::string>> rows;
    for (const auto& A : g.nonterminals)
        rows.push_back({"`" + A + "`", "`" + joinSet(g.first.at(A), g.terminals) + "`",
                        "`" + joinSet(g.follow.at(A), g.terminals) + "`",
                        "`" + joinSet(g.synch.at(A), g.terminals) + "`"});
    writeTable(out, {"Нетерминал", "FIRST", "FOLLOW", "synch (режим паники)"}, rows);

    out << "\n## Таблица M[A, a]\n\n"
        << "В ячейке — номер продукции из списка выше; `synch` — синхронизирующий символ "
           "(при ошибке нетерминал снимается со стека); пустая ячейка — ошибка, входной символ пропускается; "
           "`(k)` — ошибка, но у нетерминала единственная продукция k, начинающаяся с `<type>`; она "
           "раскрывается по умолчанию, и ошибку сообщает уже `<type>`.\n\n";
    std::vector<std::string> head = {"A \\ a"};
    for (const auto& t : g.terminals) head.push_back("`" + t + "`");
    rows.clear();
    for (const auto& A : g.nonterminals) {
        std::vector<std::string> r = {"`" + A + "`"};
        for (const auto& t : g.terminals) {
            int k = g.cell(A, t);
            int d = g.defaultProduction(A);
            if (k >= 0) r.push_back(std::to_string(k + 1));
            else if (g.synch.at(A).count(t)) r.push_back("synch");
            else if (d >= 0 && t != "$") r.push_back("(" + std::to_string(d + 1) + ")");
            else r.push_back("");
        }
        rows.push_back(r);
    }
    writeTable(out, head, rows);

    out << "\n## Проверка LL(1)\n\n";
    if (g.conflicts.empty())
        out << "Ни в одной ячейке нет двух продукций — грамматика LL(1).\n";
    else
        for (const auto& c : g.conflicts) out << "- конфликт: " << c << "\n";

    out << "\n## Режим фразы (--phrase)\n\n"
           "Ошибочные ячейки (пустые и synch) обрабатываются процедурами (проверяются по порядку):\n\n"
           "1. `M[<relop>, =]` — замена `=` на `==`;\n"
           "2. `M[<type>, id]`, если за ним снова id, — неизвестный тип, считаем его типом;\n"
           "3. `M[<statement>, id]` (и `M[<stmts>, id]`): если за id идёт `=` или `;` — объявление без типа,\n"
           "   если ещё один id — неизвестный тип; дальше разбираем как `id <assign> ;`;\n"
           "4. если следующий токен b подходит (`M[A, b]` не пусто) — текущий токен лишний, удаляем его;\n"
           "5. иначе — как в режиме паники (synch → снять A, пусто → пропустить токен).\n\n"
           "Несовпадение терминала t на вершине с токеном a: удаление a (если за ним идёт t), вставка t\n"
           "(если a может идти после t), замена a на t (если следующий токен может идти после t), иначе паника.\n";
}

// Строка исходника с номером и стрелкой под позицией ошибки (как в gcc).
static void printSourceLine(const std::vector<std::string>& lines, int line, int col) {
    if (line < 1 || line > static_cast<int>(lines.size())) return;
    const std::string& l = lines[line - 1];
    std::string prefix = std::to_string(line);
    std::cout << "  " << prefix << " | " << l << "\n  " << std::string(prefix.size(), ' ') << " | ";
    // Стрелку ставим под col-м символом: табы копируем, остальное заменяем пробелами.
    int c = 1;
    for (size_t i = 0; i < l.size() && c < col; ++i) {
        unsigned char ch = l[i];
        if ((ch & 0xC0) == 0x80) continue;
        std::cout << (ch == '\t' ? '\t' : ' ');
        ++c;
    }
    std::cout << "^\n";
}

int main(int argc, char** argv) {
    bool phrase = false, ext = false, tableOnly = false;
    // По умолчанию пишем в results/ рядом с бинарём (lab-4/cpp/results), а не в текущую папку.
    // Так результат один и тот же, откуда бы ни запускали.
    fs::path outDir = (fs::path(argv[0]).parent_path() / "results").lexically_normal(), input;
    for (int i = 1; i < argc; ++i) {  // ЦИКЛ по аргументам командной строки
        std::string a = argv[i];
        if (a == "--phrase") phrase = true;
        else if (a == "--ext") ext = true;
        else if (a == "--table") tableOnly = true;
        else if (a == "--out" && i + 1 < argc) outDir = argv[++i];
        else if (!a.empty() && a[0] != '-' && input.empty()) input = a;
        else {
            std::cerr << "неизвестный аргумент: " << a << "\n";
            return 2;
        }
    }
    if (!tableOnly && input.empty()) {
        std::cerr << "Использование: " << argv[0] << " [--phrase] [--ext] [--out DIR] файл.cl\n"
                  << "               " << argv[0] << " --table [--ext] [--out DIR]\n";
        return 2;
    }

    // 1. Грамматика → FIRST, FOLLOW, таблица M, synch.
    Grammar g = makeGrammar(ext);
    buildTables(g);
    fs::create_directories(outDir);
    const fs::path tableFile = outDir / (ext ? "parse_table_ext.md" : "parse_table.md");
    writeParseTable(g, tableFile);
    if (!g.conflicts.empty()) {
        std::cerr << "Грамматика не LL(1):\n";
        for (const auto& c : g.conflicts) std::cerr << "  " << c << "\n";
    }
    if (tableOnly) {
        std::cout << "Таблица предиктивного анализа: " << tableFile.string() << " ("
                  << (g.conflicts.empty() ? "конфликтов нет, грамматика LL(1)" : "есть конфликты") << ")\n";
        return g.conflicts.empty() ? 0 : 1;
    }

    // Каталог ifstream в Linux «открывает» и читает как пустой файл — отсекаем его явно.
    std::ifstream in(input, std::ios::binary);
    if (!in || fs::is_directory(input)) {
        std::cerr << "не удалось открыть файл " << input.string() << "\n";
        return 2;
    }
    std::stringstream buf;
    buf << in.rdbuf();
    const std::string source = buf.str();

    // 2. Лексический анализ.
    std::vector<Diagnostic> lexErrors;
    Lexer lexer(source);
    std::vector<Token> tokens = lexer.tokenize(lexErrors);

    // 3. Синтаксический анализ с восстановлением.
    Parser parser(g, tokens, phrase ? Recovery::Phrase : Recovery::Panic);
    parser.run();

    // 4. Сводим ошибки в один список по порядку в тексте.
    std::vector<Diagnostic> all = lexErrors;
    all.insert(all.end(), parser.errors.begin(), parser.errors.end());
    std::stable_sort(all.begin(), all.end(), [](const Diagnostic& x, const Diagnostic& y) {
        return x.line != y.line ? x.line < y.line : x.col < y.col;
    });

    std::vector<std::string> lines;
    {
        std::istringstream ss(source);
        for (std::string l; std::getline(ss, l);) {
            if (!l.empty() && l.back() == '\r') l.pop_back();
            lines.push_back(l);
        }
    }

    const std::string modeName = phrase ? "режим фразы" : "режим паники";
    const std::string grammarName = ext ? "расширенная (--ext)" : "из методички";
    std::cout << "Файл: " << input.string() << "\nГрамматика: " << grammarName << ", восстановление: " << modeName
              << "\n\n";
    for (size_t i = 0; i < all.size(); ++i) {  // ЦИКЛ по найденным ошибкам
        const auto& d = all[i];
        std::cout << input.string() << ":" << d.line << ":" << d.col << ": " << d.category << " ошибка ["
                  << d.type << "]: " << d.message << "\n";
        printSourceLine(lines, d.line, d.col);
        if (!d.skipped.empty()) {
            std::cout << "  при восстановлении пропущено:";
            for (const auto& s : d.skipped) std::cout << " '" << s << "'";
            std::cout << "\n";
        }
    }
    if (parser.aborted) std::cout << "Внимание: разбор прерван защитой от зацикливания\n";
    if (all.empty()) std::cout << "Программа корректна.\n";
    std::cout << (all.empty() ? "" : "\n") << "Итого ошибок: " << all.size() << " (лексических: " << lexErrors.size()
              << ", синтаксических: " << parser.errors.size() << ")\n";

    // 5. Таблица хода разбора, как в примере 4 методички.
    const fs::path traceFile = outDir / (input.stem().string() + (phrase ? ".phrase.trace.md" : ".trace.md"));
    std::ofstream out(traceFile);
    out << "# Ход разбора: " << input.filename().string() << "\n\nГрамматика: " << grammarName
        << ", восстановление: " << modeName << ".\n\n## Исходный текст\n\n```c\n"
        << source << (source.empty() || source.back() == '\n' ? "" : "\n") << "```\n\n## Ошибки (" << all.size()
        << ")\n\n";
    if (all.empty()) out << "Ошибок нет.\n";
    // Лексические — списком, синтаксические — под теми же номерами, что «Ошибка N» в таблице.
    for (const auto& d : lexErrors)
        out << "- " << d.line << ":" << d.col << " — лексическая [" << d.type << "]: " << d.message << "\n";
    if (!lexErrors.empty() && !parser.errors.empty()) out << "\n";
    for (size_t i = 0; i < parser.errors.size(); ++i) {
        const auto& d = parser.errors[i];
        out << i + 1 << ". " << d.line << ":" << d.col << " — синтаксическая [" << d.type << "]: " << d.message
            << "\n";
    }
    out << "\n## Таблица разбора\n\nСтек: дно `$` слева, вершина справа. Вход: текущий токен первый, "
           "длинный хвост сокращён до 10 токенов.\n\n";
    std::vector<std::vector<std::string>> rows;
    for (size_t i = 0; i < parser.trace.size(); ++i) {
        const auto& r = parser.trace[i];
        rows.push_back({std::to_string(i + 1), "`" + r.stack + "`", "`" + r.input + "`", r.note});
    }
    writeTable(out, {"№", "Стек", "Вход", "Примечание"}, rows);

    std::cout << "Таблица хода разбора: " << traceFile.string() << "\n"
              << "Таблица предиктивного анализа: " << tableFile.string() << "\n";
    return all.empty() ? 0 : 1;
}
