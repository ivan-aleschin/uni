// Нерекурсивный предиктивный анализатор (рис. 1 методички): входной буфер,
// стек, таблица M[A, a]. Восстановление после ошибок:
//   - режим паники (обязательный, по умолчанию);
//   - режим фразы (дополнение, флаг --phrase): ошибочные ячейки таблицы
//     (пустые и synch) обрабатываются процедурами, которые вставляют, удаляют или заменяют
//     один токен, а там, где локальная правка не подходит, — та же паника.
//
// Каждая конфигурация (стек, вход) и действие записываются в trace — из него
// получается таблица «Стек / Вход / Примечание», как в примере 4.
#pragma once

#include <map>
#include <set>
#include <string>
#include <vector>

#include "grammar.hpp"
#include "lexer.hpp"

enum class Recovery { Panic, Phrase };

struct TraceRow {
    std::string stack, input, note;
};

class Parser {
public:
    Parser(const Grammar& g, const std::vector<Token>& tokens, Recovery mode)
        : g(g), toks(tokens), mode(mode) {}

    std::vector<TraceRow> trace;
    std::vector<Diagnostic> errors;  // только синтаксические
    bool aborted = false;            // сработала защита от зацикливания (не должна)

    void run() {
        stack = {"$", g.start};
        ip = 0;
        // Защита на всякий случай: каждое действие при ошибке снимает символ со
        // стека или съедает токен, поэтому разбор конечен, но лимит не мешает.
        const size_t limit = 100000 + 50 * toks.size();

        for (size_t step = 0;; ++step) {  // ЦИКЛ repeat ... until X = $ из методички
            if (step > limit) {
                aborted = true;
                break;
            }
            TraceRow row{stackText(), inputText(), ""};
            const std::string X = stack.back();
            const Token& a = toks[ip];

            if (X == "$") {
                if (a.kind == "$") {  // X = a = $ — успешное завершение
                    row.note = errors.empty() ? "Разбор завершён, ошибок нет"
                                              : "Разбор завершён, синтаксических ошибок: " +
                                                    std::to_string(errors.size());
                    trace.push_back(row);
                    break;
                }
                // Стек пуст, а вход ещё есть: программа уже закончилась.
                row.note = report(a, "текст после конца программы",
                                  "'" + a.text + "' после закрывающей '}' функции main");
                row.note += " → пропускаем '" + a.text + "'";
                skip();
            } else if (!g.isNonterminal(X)) {
                if (X == a.kind) {  // X = a ≠ $ — снимаем X, сдвигаем вход
                    row.note = "совпадение '" + a.text + "'";
                    stack.pop_back();
                    ++ip;
                    recovering = false;  // восстановление закончено: токен принят
                } else {
                    row.note = mode == Recovery::Phrase ? phraseTerminal(X, a) : panicTerminal(X, a);
                }
            } else {
                int k = g.cell(X, a.kind);
                if (k >= 0) {  // M[X,a] = X → Y1..Yk: заменяем X на Yk..Y1
                    stack.pop_back();
                    const auto& rhs = g.prods[k].rhs;
                    for (auto it = rhs.rbegin(); it != rhs.rend(); ++it) stack.push_back(*it);
                    row.note = "`" + g.productionText(k) + "`";
                } else if (int d = defaultProduction(X, a.kind); d >= 0) {
                    // Пустая ячейка, но у X есть продукция по умолчанию: раскрываем её,
                    // ошибку обнаружит её первый символ <type>. Так "main() {...}" без
                    // типа даёт одну ошибку «нет типа», а не пропуск всей программы.
                    stack.pop_back();
                    const auto& rhs = g.prods[d].rhs;
                    for (auto it = rhs.rbegin(); it != rhs.rend(); ++it) stack.push_back(*it);
                    row.note = "`M[" + X + ", " + a.kind + "]` пусто, у " + code(X) +
                               " одна продукция — раскрываем её по умолчанию: `" + g.productionText(d) + "`";
                } else {
                    row.note = mode == Recovery::Phrase ? phraseNonterminal(X, a) : panicNonterminal(X, a);
                }
            }
            trace.push_back(row);
        }
    }

private:
    const Grammar& g;
    const std::vector<Token>& toks;
    Recovery mode;
    std::vector<std::string> stack;  // back() — вершина
    size_t ip = 0;
    // true — идёт восстановление после уже сообщённой ошибки. Пока анализатор
    // не примет хотя бы один токен, новые сообщения не выдаём (консервативная
    // стратегия из методички), иначе одна ошибка даёт лавину ложных.
    bool recovering = false;

    // Токены, на которых удобно синхронизироваться: разделители и начала
    // операторов. Если такой токен ждёт кто-то глубже в стеке, верхний
    // терминал считаем пропущенным, а не выбрасываем полезный токен со входа.
    inline static const std::set<std::string> strongSync = {";", "}", ")", "{", "for", "if", "return",
                                                            "int", "bool", "void", "$"};

    // ---------- Режим паники ----------

    // На вершине терминал t, на входе другой токен a.
    std::string panicTerminal(const std::string& t, const Token& a) {
        if (a.kind == "$") {  // вход кончился — пропускать нечего, снимаем t
            std::string n = report(a, "неожиданный конец файла", "ожидалось: " + show(t));
            stack.pop_back();
            return n + " → снимаем " + quote(t) + " со стека";
        }
        if (insertable(a.kind)) {  // РАЗВИЛКА: a подходит после t — значит, t пропущен
            std::string n = reportMissing(t, a);
            stack.pop_back();
            return n + " → снимаем " + quote(t) + " со стека";
        }
        std::string n = report(a, "неожиданный символ",
                               "'" + a.text + "', ожидалось: " + show(t) + blockHint(t, a.kind));
        skip();
        return n + " → пропускаем '" + a.text + "'";
    }

    // На вершине нетерминал A, ячейка M[A,a] пуста или synch.
    std::string panicNonterminal(const std::string& A, const Token& a) {
        const std::string cellName = "M[" + A + ", " + a.kind + "]";
        if (a.kind == "$" || g.synch.at(A).count(a.kind)) {  // РАЗВИЛКА: synch — снимаем A
            std::string n;
            if (a.kind == "$")
                n = report(a, "неожиданный конец файла", "ожидалось: " + describe(A));
            else
                n = report(a, "неполная конструкция", "перед '" + a.text + "' ожидалось: " + describe(A));
            stack.pop_back();
            return n + ", `" + cellName + "` = synch → " + code(A) + " снимается со стека";
        }
        // Пустая ячейка — пропускаем входной символ.
        std::string n = report(a, "неожиданный символ", "'" + a.text + "', ожидалось: " + describe(A));
        skip();
        return n + ", `" + cellName + "` пусто → пропускаем '" + a.text + "'";
    }

    // ---------- Режим фразы ----------
    // Локальные правки одного токена. Каждая правка снимает символ со стека
    // или съедает токен (кроме «вставки типа», после которой следующий шаг
    // гарантированно съедает id), поэтому зациклиться анализатор не может.

    std::string phraseTerminal(const std::string& t, const Token& a) {
        const std::string b = next().kind;
        if (a.kind != "$" && b == t) {  // РАЗВИЛКА: удаление — за a стоит ожидаемый t
            std::string n = report(a, "лишний символ", "'" + a.text + "' лишний, ожидаемый токен (" + show(t) + ") идёт следом");
            skip();
            return n + " → удаляем '" + a.text + "'";
        }
        if (a.kind == "$" || insertable(a.kind)) {  // РАЗВИЛКА: вставка t
            std::string n = a.kind == "$" ? report(a, "неожиданный конец файла", "ожидалось: " + show(t))
                                          : reportMissing(t, a);
            stack.pop_back();
            return n + " → вставляем " + quote(t);
        }
        if (firstBelow().count(b)) {  // РАЗВИЛКА: замена — a стоит на месте t
            std::string n = report(a, "замена символа",
                                   "'" + a.text + "' вместо " + showGen(t) + blockHint(t, a.kind));
            stack.pop_back();
            ++ip;  // токен не выброшен, а исправлен — в «пропущенные» не пишем
            return n + " → заменяем '" + a.text + "' на " + quote(t);
        }
        return panicTerminal(t, a);  // локальная правка не подошла
    }

    std::string phraseNonterminal(const std::string& A, const Token& a) {
        const std::string b = next().kind;
        // Процедура для M[<relop>, =]: типичная ошибка «= вместо ==».
        if (A == "<relop>" && a.kind == "=") {
            std::string n = report(a, "замена символа", "в сравнении '=' вместо '=='");
            stack.pop_back();
            ++ip;
            return n + " → заменяем '=' на '=='";
        }
        // Процедура для M[<type>, id], если дальше снова id: "x i = 0" —
        // вместо типа написано неизвестное слово. Заменяем его на тип.
        if (A == "<type>" && a.kind == "id" && b == "id") {
            std::string n = report(a, "неизвестный тип", "'" + a.text + "' не является типом C-light (int, bool, void)");
            stack.pop_back();
            ++ip;
            return n + " → считаем '" + a.text + "' типом";
        }
        // Процедуры для M[<statement>, id] (и <stmts>): оператор начинается с
        // идентификатора — это объявление, у которого испорчен тип:
        //   "x = 5;"     — тип пропущен, вставляем его;
        //   "float f;"   — неизвестный тип, заменяем его.
        // В обоих случаях дальше разбираем как "<тип> id <assign> ;".
        if ((A == "<statement>" || A == "<stmts>") && a.kind == "id" && (b == "=" || b == ";" || b == "id")) {
            const bool unknownType = b == "id";
            std::string n = unknownType
                ? report(a, "неизвестный тип", "'" + a.text + "' не является типом C-light (int, bool, void)")
                : report(a, "объявление без типа", "перед '" + a.text + "' не указан тип (int, bool или void)");
            stack.pop_back();
            if (A == "<stmts>") stack.push_back("<stmts>");
            stack.push_back(";");
            stack.push_back("<assign>");
            stack.push_back("id");  // следующим шагом id совпадёт с токеном
            if (unknownType) ++ip;  // неизвестный тип съедаем, как будто это int
            return n + (unknownType ? " → считаем '" + a.text + "' типом" : " → вставляем тип") +
                   ", разбираем как " + code("<declaration> ;");
        }
        if (a.kind != "$" && g.cell(A, b) >= 0) {  // РАЗВИЛКА: удаление лишнего a
            std::string n = report(a, "лишний символ", "'" + a.text + "' лишний, ожидалось: " + describe(A));
            skip();
            return n + " → удаляем '" + a.text + "'";
        }
        return panicNonterminal(A, a);
    }

    // ---------- Вспомогательное ----------

    // Продукция по умолчанию для пустой (не synch) ячейки M[A, a], или -1.
    int defaultProduction(const std::string& A, const std::string& a) const {
        if (a == "$" || g.synch.at(A).count(a)) return -1;
        return g.defaultProduction(A);
    }

    const Token& next() const { return toks[ip + 1 < toks.size() ? ip + 1 : ip]; }

    void skip() {
        if (recovering && !errors.empty()) errors.back().skipped.push_back(toks[ip].text);
        ++ip;
    }

    // FIRST того, что лежит в стеке под вершиной (что может идти после верхнего символа).
    std::set<std::string> firstBelow() const {
        std::set<std::string> res;
        for (size_t i = stack.size() - 1; i-- > 0;) {  // ЦИКЛ от вершины вниз
            const auto& s = stack[i];
            if (s == "$" || !g.isNonterminal(s)) {
                res.insert(s);
                return res;
            }
            for (const auto& x : g.first.at(s))
                if (x != EPS) res.insert(x);
            if (!g.first.at(s).count(EPS)) return res;
        }
        return res;
    }

    // Можно ли выбросить верхний терминал и продолжить с токеном a?
    // Да, если a идёт сразу после него, или если a — сильный разделитель,
    // который примет какой-то символ глубже в стеке.
    bool insertable(const std::string& a) const {
        if (firstBelow().count(a)) return true;
        if (!strongSync.count(a)) return false;
        for (size_t i = stack.size() - 1; i-- > 0;) {
            const auto& s = stack[i];
            if (s == a) return true;
            if (g.isNonterminal(s) && g.cell(s, a) >= 0) return true;
        }
        return false;
    }

    // Регистрирует ошибку. Если идёт восстановление после предыдущей,
    // новая ошибка не заводится — только пометка в таблице хода разбора.
    std::string report(const Token& at, const std::string& type, const std::string& msg) {
        return reportAt(at.line, at.col, type, msg);
    }
    std::string reportAt(int line, int col, const std::string& type, const std::string& msg) {
        if (recovering) return "восстановление";
        recovering = true;
        errors.push_back({line, col, "синтаксическая", type, msg, {}});
        return "Ошибка " + std::to_string(errors.size()) + " (" + type + ": " + msg + ")";
    }
    // «Пропущен символ» указываем сразу после предыдущего токена.
    std::string reportMissing(const std::string& t, const Token& a) {
        int line = a.line, col = a.col;
        if (ip > 0) line = toks[ip - 1].endLine, col = toks[ip - 1].endCol;
        return reportAt(line, col, "пропущен символ", "ожидалось: " + show(t) + " перед '" + a.text + "'");
    }

    // Подсказка для исходной грамматики: в { } помещается ровно один оператор.
    std::string blockHint(const std::string& t, const std::string& a) const {
        if (g.ext || t != "}" || !g.first.at("<statement>").count(a)) return "";
        return " (в C-light блок { } содержит ровно один оператор; последовательности — расширение --ext)";
    }

    // Что ожидалось вместо нетерминала: человеческое имя + токены, для которых
    // в строке M[A, ·] есть продукция.
    std::string describe(const std::string& A) const {
        static const std::map<std::string, std::string> names = {
            {"<program>", "программа"},
            {"<type>", "тип"},
            {"<statement>", "оператор"},
            {"<stmts>", "оператор или '}'"},
            {"<declaration>", "объявление"},
            {"<assign>", "инициализация или конец объявления"},
            {"<assign_end>", "значение"},
            {"<for>", "for"},
            {"<if>", "if"},
            {"<return>", "return"},
            {"<bool_expression>", "логическое выражение"},
            {"<relop>", "операция сравнения"},
        };
        std::string list;
        for (const auto& a : g.terminals)
            if (g.cell(A, a) >= 0) list += (list.empty() ? "" : ", ") + show(a);
        auto it = names.find(A);
        return (it != names.end() ? it->second : A) + " (" + list + ")";
    }

    static std::string show(const std::string& t) {
        if (t == "id") return "идентификатор";
        if (t == "num") return "число";
        if (t == "$") return "конец файла";
        return "'" + t + "'";
    }
    static std::string showGen(const std::string& t) {  // родительный падеж: «вместо числа»
        if (t == "id") return "идентификатора";
        if (t == "num") return "числа";
        return "'" + t + "'";
    }
    static std::string quote(const std::string& t) { return t == "id" || t == "num" ? t : "'" + t + "'"; }
    static std::string code(const std::string& s) { return "`" + s + "`"; }

    // Стек как в методичке: дно $ слева, вершина справа.
    std::string stackText() const {
        std::string r;
        for (const auto& s : stack) r += (r.empty() ? "" : " ") + s;
        return r;
    }
    // Остаток входа; длинный хвост сокращаем, чтобы таблица читалась.
    std::string inputText() const {
        const size_t maxShown = 10;
        std::string r;
        size_t i = ip;
        for (; i < toks.size() && toks[i].kind != "$" && i - ip < maxShown; ++i) r += toks[i].text + " ";
        if (toks[i].kind != "$") r += "… ";
        return r + "$";
    }
};
