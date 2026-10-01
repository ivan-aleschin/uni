// ТАЯК, ЛР1. Синтаксический анализатор и калькулятор арифметических выражений.
//
// Путь строки через программу:
//   строка -> tokenize() -> лексемы -> check() -> проверенные лексемы
//          -> toRpn() (алгоритм Дейкстры) -> ОПЗ -> evaluate() -> число
//
// Ошибка на любом этапе бросается как ExprError с позицией в строке,
// main ловит её и показывает, где именно ошибка.

#include <algorithm>
#include <charconv>
#include <cctype>
#include <cmath>
#include <format>
#include <iostream>
#include <string>
#include <vector>

#include <unistd.h>  // isatty: отличаем ввод с клавиатуры от printf | ./lab1

// ============================================================================
// Встроенная функция. ВСЁ, что про неё знает программа, — здесь.
// Чтобы заменить log на pow (или любую другую функцию двух аргументов),
// достаточно поменять имя, формулу и проверку области определения ниже.
// ============================================================================

constexpr int kArity = 2;  // число аргументов встроенной функции (по заданию — две)

struct BuiltinFunction {
    std::string name;                                // как функция пишется в выражении
    double (*apply)(double a, double b);             // формула
    const char* (*domainError)(double a, double b);  // nullptr, если аргументы допустимы
};

// log(a, b) — логарифм числа b по основанию a.
const BuiltinFunction kBuiltin = {
    "log",
    [](double a, double b) { return std::log(b) / std::log(a); },
    [](double a, double b) -> const char* {
        if (a <= 0 || a == 1) return "основание логарифма должно быть > 0 и не равно 1";
        if (b <= 0) return "под логарифмом должно быть положительное число";
        return nullptr;
    },
};

// Вариант для замены по требованию преподавателя — закомментировать log выше
// и раскомментировать это:
//
// const BuiltinFunction kBuiltin = {
//     "pow",
//     [](double a, double b) { return std::pow(a, b); },
//     [](double a, double b) -> const char* {
//         if (a == 0 && b < 0) return "ноль нельзя возводить в отрицательную степень";
//         if (a < 0 && b != std::floor(b)) return "отрицательное число нельзя возводить в дробную степень";
//         return nullptr;
//     },
// };

// ============================================================================
// Лексемы и ошибки
// ============================================================================

enum class Kind {
    Number,                  // действительное число: 12, 66.6, .54, 221.
    Plus, Minus, Star, Slash,  // бинарные + - * /
    Neg,                     // унарный минус (лексер его не различает, его выставляет check)
    LParen, RParen, Comma,   // ( ) ,
    Func,                    // имя встроенной функции
    End                      // конец строки — чтобы ошибку "выражение оборвалось" было куда привязать
};

struct Token {
    Kind kind;
    std::string text;  // как лексема записана во входной строке
    size_t pos;        // смещение в строке (в байтах), нужно для сообщения об ошибке
    double value = 0;  // значение, только для Number
};

struct ExprError {
    size_t pos;
    std::string message;
};

// ============================================================================
// 1. Лексический анализ: строка -> вектор лексем
// ============================================================================

// Сколько байт занимает UTF-8 символ по первому байту (нужно, чтобы
// на русской букве сообщение показывало букву целиком, а не половину).
size_t utf8Length(unsigned char c) {
    if (c >= 0xF0) return 4;
    if (c >= 0xE0) return 3;
    if (c >= 0xC0) return 2;
    return 1;
}

std::vector<Token> tokenize(const std::string& s) {
    std::vector<Token> tokens;
    size_t i = 0;
    while (i < s.size()) {  // ЦИКЛ по символам строки
        unsigned char c = s[i];
        size_t start = i;

        if (c == ' ' || c == '\t') {  // пробелы просто пропускаем
            ++i;
            continue;
        }

        // Число: подряд идущие цифры и точки. Забираем всё целиком и потом
        // проверяем, чтобы "1.2.3" было одной ошибкой, а не двумя числами.
        if (std::isdigit(c) || c == '.') {
            while (i < s.size() && (std::isdigit((unsigned char)s[i]) || s[i] == '.')) ++i;
            std::string text = s.substr(start, i - start);
            if (std::count(text.begin(), text.end(), '.') > 1 || text == ".")
                throw ExprError{start, std::format("некорректное число '{}'", text)};
            double value = 0;
            auto [end, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
            if (ec == std::errc::result_out_of_range) {
                // from_chars так отвечает и на 1000…0, и на 0.000…01: различаем по целой части
                bool huge = text.find_first_of("123456789") < text.find('.');
                throw ExprError{start, std::format("слишком {} число '{}'",
                                                   huge ? "большое" : "близкое к нулю", text)};
            }
            tokens.push_back({Kind::Number, text, start, value});
            continue;
        }

        // Имя: буквы, цифры, '_'. Допустимо только имя встроенной функции.
        if (std::isalpha(c) || c == '_') {
            while (i < s.size() && (std::isalnum((unsigned char)s[i]) || s[i] == '_')) ++i;
            std::string name = s.substr(start, i - start);
            if (name != kBuiltin.name)
                throw ExprError{start, std::format("неизвестное имя '{}' (есть только функция {})",
                                                   name, kBuiltin.name)};
            tokens.push_back({Kind::Func, name, start});
            continue;
        }

        // Односимвольные лексемы
        Kind kind;
        switch (c) {  // РАЗВИЛКА по символу
            case '+': kind = Kind::Plus; break;
            case '-': kind = Kind::Minus; break;
            case '*': kind = Kind::Star; break;
            case '/': kind = Kind::Slash; break;
            case '(': kind = Kind::LParen; break;
            case ')': kind = Kind::RParen; break;
            case ',': kind = Kind::Comma; break;
            default:
                throw ExprError{start, std::format("недопустимый символ '{}'",
                                                   s.substr(start, utf8Length(c)))};
        }
        tokens.push_back({kind, std::string(1, (char)c), start});
        ++i;
    }
    tokens.push_back({Kind::End, "конец строки", s.size()});
    return tokens;
}

// ============================================================================
// 2. Синтаксическая проверка
//
// Идём по лексемам и помним одно: что сейчас ожидается — ОПЕРАНД (число,
// '(', функция, унарный минус) или ОПЕРАЦИЯ (+ - * /, ')', ',', конец).
// Плюс стек открытых скобок: для скобки функции считаем аргументы.
// Попутно минус в позиции операнда помечается как унарный (Kind::Neg).
// ============================================================================

bool isOperator(Kind k) {
    return k == Kind::Plus || k == Kind::Minus || k == Kind::Star || k == Kind::Slash ||
           k == Kind::Neg;
}

// Текст ошибки "здесь должен был быть операнд, а стоит cur".
// Разбираем частные случаи, чтобы сообщение было понятным.
std::string missingOperandMessage(const std::vector<Token>& t, size_t i) {
    const Token& cur = t[i];
    if (i == 0)
        return cur.kind == Kind::End ? "пустое выражение"
                                     : std::format("выражение не может начинаться с '{}'", cur.text);
    const Token& prev = t[i - 1];
    if (cur.kind == Kind::End)
        return std::format("выражение оборвалось: после '{}' ожидается операнд", prev.text);
    if (isOperator(prev.kind))
        return std::format("два знака операции подряд: '{}' и '{}'", prev.text, cur.text);
    if (prev.kind == Kind::LParen && cur.kind == Kind::RParen)
        return (i >= 2 && t[i - 2].kind == Kind::Func)
                   ? std::format("у функции {} нет аргументов", t[i - 2].text)
                   : "пустые скобки '()'";
    if (cur.kind == Kind::Comma || cur.kind == Kind::RParen)
        return "пропущен аргумент функции";  // "log(,2)", "log(2,)"
    return std::format("после '{}' ожидается операнд, а стоит '{}'", prev.text, cur.text);
}

void check(std::vector<Token>& t) {
    struct Paren {
        size_t pos;   // где открыта — для ошибки "не закрыта"
        bool isFunc;  // скобка функции?
        int args;     // сколько аргументов уже начато
    };
    std::vector<Paren> parens;
    bool expectOperand = true;

    for (size_t i = 0; i < t.size(); ++i) {  // ЦИКЛ по лексемам
        Token& cur = t[i];

        if (expectOperand) {  // РАЗВИЛКА: ждём операнд
            switch (cur.kind) {
                case Kind::Number:
                    expectOperand = false;
                    break;
                case Kind::Minus:  // минус там, где ждём операнд, — унарный
                    cur.kind = Kind::Neg;
                    break;
                case Kind::LParen:
                    parens.push_back({cur.pos, false, 0});
                    break;
                case Kind::Func:  // после имени функции обязательно '('
                    if (t[i + 1].kind != Kind::LParen)
                        throw ExprError{t[i + 1].pos,
                                        std::format("после имени функции {} ожидается '('", cur.text)};
                    ++i;
                    parens.push_back({t[i].pos, true, 1});
                    break;
                default:
                    throw ExprError{cur.pos, missingOperandMessage(t, i)};
            }
        } else {  // РАЗВИЛКА: ждём операцию
            switch (cur.kind) {
                case Kind::Plus:
                case Kind::Minus:
                case Kind::Star:
                case Kind::Slash:
                    expectOperand = true;
                    break;
                case Kind::RParen:
                    if (parens.empty())
                        throw ExprError{cur.pos, "лишняя ')': для неё нет парной '('"};
                    if (parens.back().isFunc && parens.back().args != kArity)
                        throw ExprError{cur.pos,
                                        std::format("функция {} принимает {} аргумента, а передано {}",
                                                    kBuiltin.name, kArity, parens.back().args)};
                    parens.pop_back();
                    break;
                case Kind::Comma:
                    if (parens.empty() || !parens.back().isFunc)
                        throw ExprError{cur.pos, "запятая вне скобок функции"};
                    ++parens.back().args;
                    expectOperand = true;
                    break;
                case Kind::End:
                    if (!parens.empty())
                        throw ExprError{parens.back().pos, "не закрыта '(': не хватает ')'"};
                    break;
                default:  // число, '(' или функция сразу после операнда
                    throw ExprError{cur.pos, std::format("пропущен знак операции между '{}' и '{}'",
                                                         t[i - 1].text, cur.text)};
            }
        }
    }
}

// ============================================================================
// 3. Перевод в обратную польскую запись (алгоритм Дейкстры)
//
// Стековые приоритеты — табл. 1 методички, дополненная унарным минусом
// и функцией:  ( ) — 1,  + - — 2,  * / — 3,  унарный минус — 4,  функция — 5.
// ============================================================================

int priority(Kind k) {
    switch (k) {
        case Kind::LParen: case Kind::RParen: return 1;
        case Kind::Plus: case Kind::Minus: return 2;
        case Kind::Star: case Kind::Slash: return 3;
        case Kind::Neg: return 4;
        case Kind::Func: return 5;
        default: return 0;
    }
}

std::string joinTexts(const std::vector<Token>& v, const char* neg) {
    std::string r;
    for (const Token& t : v) {
        if (!r.empty()) r += ' ';
        r += t.kind == Kind::Neg ? neg : t.text;
    }
    return r;
}

// Строку проверили в check(), поэтому здесь ошибок быть не может.
// trace = true печатает таблицу как на рис. 2 методички.
std::vector<Token> toRpn(const std::vector<Token>& t, bool trace) {
    std::vector<Token> out, stack;
    auto popToOut = [&] {
        out.push_back(stack.back());
        stack.pop_back();
    };

    if (trace) std::cout << std::format("  {:<14}{:<22}{}\n", "символ", "стек (верх справа)", "выход");

    for (const Token& cur : t) {  // ЦИКЛ по лексемам
        switch (cur.kind) {  // РАЗВИЛКА по типу лексемы
            case Kind::Number:  // операнд — сразу в выходную строку
                out.push_back(cur);
                break;
            case Kind::LParen:  // правило c): '(' — в стек
            case Kind::Func:    // функция и унарный минус префиксные: перед ними
            case Kind::Neg:     // в стеке нет ничего, что пора вычислять, — просто в стек
                stack.push_back(cur);
                break;
            case Kind::Comma:  // запятая закрывает аргумент: выталкиваем до '(' функции
                while (stack.back().kind != Kind::LParen) popToOut();
                break;
            case Kind::RParen:  // правило d): выталкиваем до '(', скобки уничтожают друг друга
                while (stack.back().kind != Kind::LParen) popToOut();
                stack.pop_back();
                if (!stack.empty() && stack.back().kind == Kind::Func) popToOut();
                break;
            case Kind::End:  // конец строки: всё, что осталось, — в выход
                while (!stack.empty()) popToOut();
                break;
            default:  // бинарная операция, правило b): выталкиваем всё с приоритетом >=
                while (!stack.empty() && priority(stack.back().kind) >= priority(cur.kind))
                    popToOut();
                stack.push_back(cur);
        }
        if (trace)
            std::cout << std::format("  {:<14}{:<22}{}\n", cur.kind == Kind::Neg ? "-(унарный)" : cur.text,
                                     joinTexts(stack, "~"), joinTexts(out, "~"));
    }
    return out;
}

// ============================================================================
// 4. Вычисление ОПЗ на стеке
// ============================================================================

std::string formatNumber(double x) {
    if (x == 0) x = 0;  // чтобы не печатать "-0"
    return std::format("{:.12g}", x);
}

double evaluate(const std::vector<Token>& rpn) {
    std::vector<double> stack;
    auto pop = [&] {
        double v = stack.back();
        stack.pop_back();
        return v;
    };

    for (const Token& t : rpn) {  // ЦИКЛ по ОПЗ слева направо
        switch (t.kind) {  // РАЗВИЛКА
            case Kind::Number:
                stack.push_back(t.value);
                break;
            case Kind::Neg:
                stack.back() = -stack.back();
                break;
            case Kind::Func: {
                double b = pop(), a = pop();  // на вершине — последний аргумент
                if (const char* err = kBuiltin.domainError(a, b))
                    throw ExprError{t.pos, std::format("{}({}, {}): {}", kBuiltin.name,
                                                       formatNumber(a), formatNumber(b), err)};
                stack.push_back(kBuiltin.apply(a, b));
                break;
            }
            default: {  // бинарная операция
                double b = pop(), a = pop();
                switch (t.kind) {
                    case Kind::Plus: stack.push_back(a + b); break;
                    case Kind::Minus: stack.push_back(a - b); break;
                    case Kind::Star: stack.push_back(a * b); break;
                    default:
                        if (b == 0) throw ExprError{t.pos, "деление на ноль"};
                        stack.push_back(a / b);
                }
            }
        }
        if (!std::isfinite(stack.back()))
            throw ExprError{t.pos, "переполнение: результат не помещается в double"};
    }
    return stack.back();
}

// ============================================================================
// Ввод-вывод
// ============================================================================

// Отступ для стрелки ^ под символом с байтовым смещением bytePos: по пробелу
// на каждый символ левее (русская буква — 2 байта, но один символ), табуляция
// копируется как есть, иначе стрелка съедет. Номер символа = длина отступа + 1.
std::string caretPad(const std::string& s, size_t bytePos) {
    std::string pad;
    for (size_t i = 0; i < bytePos && i < s.size(); ++i)
        if (((unsigned char)s[i] & 0xC0) != 0x80)  // не байт-продолжение UTF-8
            pad += s[i] == '\t' ? '\t' : ' ';
    return pad;
}

void process(const std::string& line, bool trace) {
    const char* stage = "Синтаксическая ошибка";
    try {
        std::vector<Token> tokens = tokenize(line);
        check(tokens);
        std::cout << "Выражение корректно.\n";
        std::vector<Token> rpn = toRpn(tokens, trace);
        std::cout << "ОПЗ: " << joinTexts(rpn, "~") << '\n';
        stage = "Ошибка вычисления";
        double result = evaluate(rpn);
        std::cout << "Результат: " << formatNumber(result) << '\n';
    } catch (const ExprError& e) {
        std::string pad = caretPad(line, e.pos);
        std::cout << std::format("{} в позиции {}: {}\n", stage, pad.size() + 1, e.message);
        std::cout << "  " << line << '\n';
        std::cout << "  " << pad << "^\n";
    }
}

int main(int argc, char** argv) {
    bool trace = argc > 1 && std::string(argv[1]) == "--trace";
    bool interactive = isatty(STDIN_FILENO);

    if (interactive)
        std::cout << std::format("Калькулятор: + - * /, скобки, числа вида 12, 66.6, .54, 221., "
                                 "функция {}(a, b).\nПустая строка или Ctrl+D — выход.\n",
                                 kBuiltin.name);

    std::string line;
    while (true) {  // ЦИКЛ: строка за строкой до EOF (с клавиатуры — и до пустой строки)
        if (interactive) std::cout << "> " << std::flush;
        if (!std::getline(std::cin, line)) break;
        if (!line.empty() && line.back() == '\r') line.pop_back();  // файлы из Windows
        if (line.empty() && interactive) break;  // из файла пустая строка — это "пустое выражение"
        if (!interactive) std::cout << "> " << line << '\n';  // эхо, чтобы в выводе было видно выражение
        process(line, trace);
        std::cout << '\n';
    }
    return 0;
}
