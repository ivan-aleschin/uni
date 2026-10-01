// Лексический анализатор C-light.
//
// В грамматике из методички есть два уровня. <identifier>, <number>, <character>,
// <digit>, <id_end>, <number_end> записаны через конкатенацию без пробелов
// (<N1><N2>) и задают регулярные множества строк: это работа лексера (конечного
// автомата), а не LL(1)-анализатора. Остальные правила записаны через пробельные
// символы (<N1>   <N2>) и работают уже с токенами — их разбирает parser.hpp.
//
// Лексер превращает текст в поток токенов с позициями и сам находит лексические
// ошибки. После лексической ошибки он не останавливается: недопустимый символ
// выбрасывается, а «испорченный» идентификатор или число всё равно выдаётся
// токеном id/num, чтобы синтаксический анализ продолжался без лишних ошибок.
#pragma once

#include <set>
#include <string>
#include <vector>

// Токен. kind — имя терминала грамматики ("int", "id", "num", "(", "==", "$"),
// text — как он записан в исходнике. line/col — начало токена (с единицы),
// endLine/endCol — позиция сразу за ним: туда указываем, когда сообщаем
// «пропущена ';'», чтобы стрелка стояла после предыдущего токена, как в gcc.
struct Token {
    std::string kind, text;
    int line = 1, col = 1;
    int endLine = 1, endCol = 1;
};

// Сообщение об ошибке, общее для лексера и парсера.
struct Diagnostic {
    int line = 0, col = 0;
    std::string category;              // "лексическая" или "синтаксическая"
    std::string type;                  // тип ошибки (см. README, раздел «Типы ошибок»)
    std::string message;               // понятное пояснение
    std::vector<std::string> skipped;  // токены, пропущенные при восстановлении
};

class Lexer {
public:
    explicit Lexer(const std::string& source) : s(source) {}

    std::vector<Token> tokenize(std::vector<Diagnostic>& errors) {
        std::vector<Token> tokens;
        // Ключевые слова зарезервированы, как в C: по символьной грамматике
        // слово "int" подходит и под <identifier>, но тогда "int int = 5"
        // стало бы неоднозначным. 'main' тоже считаем ключевым словом —
        // в <program> он стоит как терминал.
        static const std::set<std::string> keywords = {
            "int", "bool", "void", "main", "for", "if", "return"};

        while (pos < s.size()) {
            char c = peek();

            // Пробельные символы — как в C. Комментарии в C тоже считаются
            // пробельными символами, поэтому // и /* */ просто пропускаем.
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f') {
                advance();
                continue;
            }
            if (c == '/' && peek(1) == '/') {
                while (pos < s.size() && peek() != '\n') advance();
                continue;
            }
            if (c == '/' && peek(1) == '*') {
                int l = line, cl = col;
                advance(), advance();
                bool closed = false;
                while (pos < s.size()) {  // ЦИКЛ до "*/" или конца файла
                    if (peek() == '*' && peek(1) == '/') {
                        advance(), advance();
                        closed = true;
                        break;
                    }
                    advance();
                }
                if (!closed)
                    error(errors, l, cl, "незакрытый комментарий",
                          "комментарий '/*' не закрыт до конца файла");
                continue;
            }

            Token t;
            t.line = line;
            t.col = col;

            if (isLetter(c)) {
                // <identifier>: <character><id_end> — только буквы и '_'.
                // Читаем и цифры тоже, чтобы "x1" дал одну ошибку, а не две.
                bool hasDigit = false;
                while (isLetter(peek()) || isDigit(peek())) {
                    hasDigit |= isDigit(peek());
                    t.text += peek();
                    advance();
                }
                t.kind = keywords.count(t.text) ? t.text : "id";
                if (hasDigit)
                    error(errors, t.line, t.col, "неверный идентификатор",
                          "'" + t.text + "': по грамматике C-light идентификатор состоит "
                          "только из букв и '_', цифры не допускаются");
            } else if (isDigit(c)) {
                // <number>: <digit><number_end> — только цифры.
                bool bad = false;
                while (isLetter(peek()) || isDigit(peek())) {
                    bad |= !isDigit(peek());
                    t.text += peek();
                    advance();
                }
                t.kind = "num";
                if (bad)
                    error(errors, t.line, t.col, "неверное число",
                          "'" + t.text + "': число может содержать только цифры");
            } else if (c == '(' || c == ')' || c == '{' || c == '}' || c == ';') {
                t.text = t.kind = std::string(1, c);
                advance();
            } else if (c == '=') {  // '=' или '=='
                advance();
                if (peek() == '=') advance(), t.text = "==";
                else t.text = "=";
                t.kind = t.text;
            } else if (c == '<' || c == '>') {
                // В C-light есть только '<' и '>'. "<=" и ">=" — частая ошибка
                // человека, пишущего на C: сообщаем и выдаём '<' / '>'.
                advance();
                t.text = t.kind = std::string(1, c);
                if (peek() == '=') {
                    advance();
                    error(errors, t.line, t.col, "неподдерживаемая операция",
                          std::string("операции '") + c + "=' нет в C-light (есть только <, >, ==, !=); "
                          "считаем, что написано '" + c + "'");
                }
            } else if (c == '!') {
                advance();
                t.text = t.kind = "!=";
                if (peek() == '=') advance();
                else
                    error(errors, t.line, t.col, "неподдерживаемая операция",
                          "одиночный '!' (в C-light есть только '!='); считаем, что написано '!='");
            } else {
                // Чужой символ (',', '+', '@', кириллица...). UTF-8 символ может
                // занимать несколько байт — забираем его целиком.
                size_t start = pos;
                advance();
                while (pos < s.size() && (static_cast<unsigned char>(s[pos]) & 0xC0) == 0x80) advance();
                error(errors, t.line, t.col, "недопустимый символ",
                      "символ '" + s.substr(start, pos - start) + "' не входит в алфавит C-light, пропущен");
                continue;
            }
            t.endLine = line;
            t.endCol = col;
            tokens.push_back(t);
        }

        // Маркер конца входа $, как в методичке.
        Token end;
        end.kind = "$";
        end.text = "$";
        end.line = end.endLine = line;
        end.col = end.endCol = col;
        tokens.push_back(end);
        return tokens;
    }

private:
    const std::string& s;
    size_t pos = 0;
    int line = 1, col = 1;

    char peek(size_t k = 0) const { return pos + k < s.size() ? s[pos + k] : '\0'; }

    // Сдвиг на один байт. Столбец считаем в символах, а не в байтах:
    // байты-продолжения UTF-8 (10xxxxxx) столбец не увеличивают.
    void advance() {
        unsigned char c = s[pos++];
        if (c == '\n') {
            ++line;
            col = 1;
        } else if ((c & 0xC0) != 0x80) {
            ++col;
        }
    }

    static bool isLetter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'; }
    static bool isDigit(char c) { return c >= '0' && c <= '9'; }

    static void error(std::vector<Diagnostic>& errors, int l, int c, const std::string& type,
                      const std::string& msg) {
        errors.push_back({l, c, "лексическая", type, msg, {}});
    }
};
