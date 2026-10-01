# Ход разбора: ext_errors.cl

Грамматика: расширенная (--ext), восстановление: режим фразы.

## Исходный текст

```c
// Расширенная грамматика, по ошибке почти в каждой строке.
// флаги: --ext
// ожидается: panic=8 phrase=8
int main() {
    int a = 1
    bool = 5;
    x = 3;
    for (int i = 0; i < 10;) {
        if (i = a) return 0;
        return y;
    }
    float f = 2;
    if a < b) return 1;
}
// Ошибки: 5 — нет ';', 6 — нет имени, 7 — нет типа, 8 — число справа от '<',
// 9 — '=' вместо '==', 10 — return с идентификатором, 12 — float не тип C-light,
// 13 — нет '(' после if.
```

## Ошибки (8)

1. 5:14 — синтаксическая [пропущен символ]: ожидалось: ';' перед 'bool'
2. 6:9 — синтаксическая [пропущен символ]: ожидалось: идентификатор перед '='
3. 7:5 — синтаксическая [объявление без типа]: перед 'x' не указан тип (int, bool или void)
4. 8:25 — синтаксическая [замена символа]: '10' вместо идентификатора
5. 9:15 — синтаксическая [замена символа]: в сравнении '=' вместо '=='
6. 10:16 — синтаксическая [замена символа]: 'y' вместо числа
7. 12:5 — синтаксическая [неизвестный тип]: 'float' не является типом C-light (int, bool, void)
8. 13:7 — синтаксическая [пропущен символ]: ожидалось: '(' перед 'a'

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                                  | Вход                                    | Примечание                                                                                                                               |
|-----|-----------------------------------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | `$ <program>`                                                         | `int main ( ) { int a = 1 bool … $`     | `<program> → <type> main ( ) { <stmts> }`                                                                                                |
| 2   | `$ } <stmts> { ) ( main <type>`                                       | `int main ( ) { int a = 1 bool … $`     | `<type> → int`                                                                                                                           |
| 3   | `$ } <stmts> { ) ( main int`                                          | `int main ( ) { int a = 1 bool … $`     | совпадение 'int'                                                                                                                         |
| 4   | `$ } <stmts> { ) ( main`                                              | `main ( ) { int a = 1 bool = … $`       | совпадение 'main'                                                                                                                        |
| 5   | `$ } <stmts> { ) (`                                                   | `( ) { int a = 1 bool = 5 … $`          | совпадение '('                                                                                                                           |
| 6   | `$ } <stmts> { )`                                                     | `) { int a = 1 bool = 5 ; … $`          | совпадение ')'                                                                                                                           |
| 7   | `$ } <stmts> {`                                                       | `{ int a = 1 bool = 5 ; x … $`          | совпадение '{'                                                                                                                           |
| 8   | `$ } <stmts>`                                                         | `int a = 1 bool = 5 ; x = … $`          | `<stmts> → <statement> <stmts>`                                                                                                          |
| 9   | `$ } <stmts> <statement>`                                             | `int a = 1 bool = 5 ; x = … $`          | `<statement> → <declaration> ;`                                                                                                          |
| 10  | `$ } <stmts> ; <declaration>`                                         | `int a = 1 bool = 5 ; x = … $`          | `<declaration> → <type> id <assign>`                                                                                                     |
| 11  | `$ } <stmts> ; <assign> id <type>`                                    | `int a = 1 bool = 5 ; x = … $`          | `<type> → int`                                                                                                                           |
| 12  | `$ } <stmts> ; <assign> id int`                                       | `int a = 1 bool = 5 ; x = … $`          | совпадение 'int'                                                                                                                         |
| 13  | `$ } <stmts> ; <assign> id`                                           | `a = 1 bool = 5 ; x = 3 … $`            | совпадение 'a'                                                                                                                           |
| 14  | `$ } <stmts> ; <assign>`                                              | `= 1 bool = 5 ; x = 3 ; … $`            | `<assign> → = <assign_end>`                                                                                                              |
| 15  | `$ } <stmts> ; <assign_end> =`                                        | `= 1 bool = 5 ; x = 3 ; … $`            | совпадение '='                                                                                                                           |
| 16  | `$ } <stmts> ; <assign_end>`                                          | `1 bool = 5 ; x = 3 ; for … $`          | `<assign_end> → num`                                                                                                                     |
| 17  | `$ } <stmts> ; num`                                                   | `1 bool = 5 ; x = 3 ; for … $`          | совпадение '1'                                                                                                                           |
| 18  | `$ } <stmts> ;`                                                       | `bool = 5 ; x = 3 ; for ( … $`          | Ошибка 1 (пропущен символ: ожидалось: ';' перед 'bool') → вставляем ';'                                                                  |
| 19  | `$ } <stmts>`                                                         | `bool = 5 ; x = 3 ; for ( … $`          | `<stmts> → <statement> <stmts>`                                                                                                          |
| 20  | `$ } <stmts> <statement>`                                             | `bool = 5 ; x = 3 ; for ( … $`          | `<statement> → <declaration> ;`                                                                                                          |
| 21  | `$ } <stmts> ; <declaration>`                                         | `bool = 5 ; x = 3 ; for ( … $`          | `<declaration> → <type> id <assign>`                                                                                                     |
| 22  | `$ } <stmts> ; <assign> id <type>`                                    | `bool = 5 ; x = 3 ; for ( … $`          | `<type> → bool`                                                                                                                          |
| 23  | `$ } <stmts> ; <assign> id bool`                                      | `bool = 5 ; x = 3 ; for ( … $`          | совпадение 'bool'                                                                                                                        |
| 24  | `$ } <stmts> ; <assign> id`                                           | `= 5 ; x = 3 ; for ( int … $`           | Ошибка 2 (пропущен символ: ожидалось: идентификатор перед '=') → вставляем id                                                            |
| 25  | `$ } <stmts> ; <assign>`                                              | `= 5 ; x = 3 ; for ( int … $`           | `<assign> → = <assign_end>`                                                                                                              |
| 26  | `$ } <stmts> ; <assign_end> =`                                        | `= 5 ; x = 3 ; for ( int … $`           | совпадение '='                                                                                                                           |
| 27  | `$ } <stmts> ; <assign_end>`                                          | `5 ; x = 3 ; for ( int i … $`           | `<assign_end> → num`                                                                                                                     |
| 28  | `$ } <stmts> ; num`                                                   | `5 ; x = 3 ; for ( int i … $`           | совпадение '5'                                                                                                                           |
| 29  | `$ } <stmts> ;`                                                       | `; x = 3 ; for ( int i = … $`           | совпадение ';'                                                                                                                           |
| 30  | `$ } <stmts>`                                                         | `x = 3 ; for ( int i = 0 … $`           | Ошибка 3 (объявление без типа: перед 'x' не указан тип (int, bool или void)) → вставляем тип, разбираем как `<declaration> ;`            |
| 31  | `$ } <stmts> ; <assign> id`                                           | `x = 3 ; for ( int i = 0 … $`           | совпадение 'x'                                                                                                                           |
| 32  | `$ } <stmts> ; <assign>`                                              | `= 3 ; for ( int i = 0 ; … $`           | `<assign> → = <assign_end>`                                                                                                              |
| 33  | `$ } <stmts> ; <assign_end> =`                                        | `= 3 ; for ( int i = 0 ; … $`           | совпадение '='                                                                                                                           |
| 34  | `$ } <stmts> ; <assign_end>`                                          | `3 ; for ( int i = 0 ; i … $`           | `<assign_end> → num`                                                                                                                     |
| 35  | `$ } <stmts> ; num`                                                   | `3 ; for ( int i = 0 ; i … $`           | совпадение '3'                                                                                                                           |
| 36  | `$ } <stmts> ;`                                                       | `; for ( int i = 0 ; i < … $`           | совпадение ';'                                                                                                                           |
| 37  | `$ } <stmts>`                                                         | `for ( int i = 0 ; i < 10 … $`          | `<stmts> → <statement> <stmts>`                                                                                                          |
| 38  | `$ } <stmts> <statement>`                                             | `for ( int i = 0 ; i < 10 … $`          | `<statement> → <for> <statement>`                                                                                                        |
| 39  | `$ } <stmts> <statement> <for>`                                       | `for ( int i = 0 ; i < 10 … $`          | `<for> → for ( <declaration> ; <bool_expression> ; )`                                                                                    |
| 40  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( int i = 0 ; i < 10 … $`          | совпадение 'for'                                                                                                                         |
| 41  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> (`     | `( int i = 0 ; i < 10 ; … $`            | совпадение '('                                                                                                                           |
| 42  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration>`       | `int i = 0 ; i < 10 ; ) … $`            | `<declaration> → <type> id <assign>`                                                                                                     |
| 43  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id <type>`  | `int i = 0 ; i < 10 ; ) … $`            | `<type> → int`                                                                                                                           |
| 44  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id int`     | `int i = 0 ; i < 10 ; ) … $`            | совпадение 'int'                                                                                                                         |
| 45  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id`         | `i = 0 ; i < 10 ; ) { … $`              | совпадение 'i'                                                                                                                           |
| 46  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign>`            | `= 0 ; i < 10 ; ) { if … $`             | `<assign> → = <assign_end>`                                                                                                              |
| 47  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 0 ; i < 10 ; ) { if … $`             | совпадение '='                                                                                                                           |
| 48  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end>`        | `0 ; i < 10 ; ) { if ( … $`             | `<assign_end> → num`                                                                                                                     |
| 49  | `$ } <stmts> <statement> ) ; <bool_expression> ; num`                 | `0 ; i < 10 ; ) { if ( … $`             | совпадение '0'                                                                                                                           |
| 50  | `$ } <stmts> <statement> ) ; <bool_expression> ;`                     | `; i < 10 ; ) { if ( i … $`             | совпадение ';'                                                                                                                           |
| 51  | `$ } <stmts> <statement> ) ; <bool_expression>`                       | `i < 10 ; ) { if ( i = … $`             | `<bool_expression> → id <relop> id`                                                                                                      |
| 52  | `$ } <stmts> <statement> ) ; id <relop> id`                           | `i < 10 ; ) { if ( i = … $`             | совпадение 'i'                                                                                                                           |
| 53  | `$ } <stmts> <statement> ) ; id <relop>`                              | `< 10 ; ) { if ( i = a … $`             | `<relop> → <`                                                                                                                            |
| 54  | `$ } <stmts> <statement> ) ; id <`                                    | `< 10 ; ) { if ( i = a … $`             | совпадение '<'                                                                                                                           |
| 55  | `$ } <stmts> <statement> ) ; id`                                      | `10 ; ) { if ( i = a ) … $`             | Ошибка 4 (замена символа: '10' вместо идентификатора) → заменяем '10' на id                                                              |
| 56  | `$ } <stmts> <statement> ) ;`                                         | `; ) { if ( i = a ) return … $`         | совпадение ';'                                                                                                                           |
| 57  | `$ } <stmts> <statement> )`                                           | `) { if ( i = a ) return 0 … $`         | совпадение ')'                                                                                                                           |
| 58  | `$ } <stmts> <statement>`                                             | `{ if ( i = a ) return 0 ; … $`         | `<statement> → { <stmts> }`                                                                                                              |
| 59  | `$ } <stmts> } <stmts> {`                                             | `{ if ( i = a ) return 0 ; … $`         | совпадение '{'                                                                                                                           |
| 60  | `$ } <stmts> } <stmts>`                                               | `if ( i = a ) return 0 ; return … $`    | `<stmts> → <statement> <stmts>`                                                                                                          |
| 61  | `$ } <stmts> } <stmts> <statement>`                                   | `if ( i = a ) return 0 ; return … $`    | `<statement> → <if> <statement>`                                                                                                         |
| 62  | `$ } <stmts> } <stmts> <statement> <if>`                              | `if ( i = a ) return 0 ; return … $`    | `<if> → if ( <bool_expression> )`                                                                                                        |
| 63  | `$ } <stmts> } <stmts> <statement> ) <bool_expression> ( if`          | `if ( i = a ) return 0 ; return … $`    | совпадение 'if'                                                                                                                          |
| 64  | `$ } <stmts> } <stmts> <statement> ) <bool_expression> (`             | `( i = a ) return 0 ; return y … $`     | совпадение '('                                                                                                                           |
| 65  | `$ } <stmts> } <stmts> <statement> ) <bool_expression>`               | `i = a ) return 0 ; return y ; … $`     | `<bool_expression> → id <relop> id`                                                                                                      |
| 66  | `$ } <stmts> } <stmts> <statement> ) id <relop> id`                   | `i = a ) return 0 ; return y ; … $`     | совпадение 'i'                                                                                                                           |
| 67  | `$ } <stmts> } <stmts> <statement> ) id <relop>`                      | `= a ) return 0 ; return y ; } … $`     | Ошибка 5 (замена символа: в сравнении '=' вместо '==') → заменяем '=' на '=='                                                            |
| 68  | `$ } <stmts> } <stmts> <statement> ) id`                              | `a ) return 0 ; return y ; } float … $` | совпадение 'a'                                                                                                                           |
| 69  | `$ } <stmts> } <stmts> <statement> )`                                 | `) return 0 ; return y ; } float f … $` | совпадение ')'                                                                                                                           |
| 70  | `$ } <stmts> } <stmts> <statement>`                                   | `return 0 ; return y ; } float f = … $` | `<statement> → <return>`                                                                                                                 |
| 71  | `$ } <stmts> } <stmts> <return>`                                      | `return 0 ; return y ; } float f = … $` | `<return> → return num ;`                                                                                                                |
| 72  | `$ } <stmts> } <stmts> ; num return`                                  | `return 0 ; return y ; } float f = … $` | совпадение 'return'                                                                                                                      |
| 73  | `$ } <stmts> } <stmts> ; num`                                         | `0 ; return y ; } float f = 2 … $`      | совпадение '0'                                                                                                                           |
| 74  | `$ } <stmts> } <stmts> ;`                                             | `; return y ; } float f = 2 ; … $`      | совпадение ';'                                                                                                                           |
| 75  | `$ } <stmts> } <stmts>`                                               | `return y ; } float f = 2 ; if … $`     | `<stmts> → <statement> <stmts>`                                                                                                          |
| 76  | `$ } <stmts> } <stmts> <statement>`                                   | `return y ; } float f = 2 ; if … $`     | `<statement> → <return>`                                                                                                                 |
| 77  | `$ } <stmts> } <stmts> <return>`                                      | `return y ; } float f = 2 ; if … $`     | `<return> → return num ;`                                                                                                                |
| 78  | `$ } <stmts> } <stmts> ; num return`                                  | `return y ; } float f = 2 ; if … $`     | совпадение 'return'                                                                                                                      |
| 79  | `$ } <stmts> } <stmts> ; num`                                         | `y ; } float f = 2 ; if a … $`          | Ошибка 6 (замена символа: 'y' вместо числа) → заменяем 'y' на num                                                                        |
| 80  | `$ } <stmts> } <stmts> ;`                                             | `; } float f = 2 ; if a < … $`          | совпадение ';'                                                                                                                           |
| 81  | `$ } <stmts> } <stmts>`                                               | `} float f = 2 ; if a < b … $`          | `<stmts> → ε`                                                                                                                            |
| 82  | `$ } <stmts> }`                                                       | `} float f = 2 ; if a < b … $`          | совпадение '}'                                                                                                                           |
| 83  | `$ } <stmts>`                                                         | `float f = 2 ; if a < b ) … $`          | Ошибка 7 (неизвестный тип: 'float' не является типом C-light (int, bool, void)) → считаем 'float' типом, разбираем как `<declaration> ;` |
| 84  | `$ } <stmts> ; <assign> id`                                           | `f = 2 ; if a < b ) return … $`         | совпадение 'f'                                                                                                                           |
| 85  | `$ } <stmts> ; <assign>`                                              | `= 2 ; if a < b ) return 1 … $`         | `<assign> → = <assign_end>`                                                                                                              |
| 86  | `$ } <stmts> ; <assign_end> =`                                        | `= 2 ; if a < b ) return 1 … $`         | совпадение '='                                                                                                                           |
| 87  | `$ } <stmts> ; <assign_end>`                                          | `2 ; if a < b ) return 1 ; … $`         | `<assign_end> → num`                                                                                                                     |
| 88  | `$ } <stmts> ; num`                                                   | `2 ; if a < b ) return 1 ; … $`         | совпадение '2'                                                                                                                           |
| 89  | `$ } <stmts> ;`                                                       | `; if a < b ) return 1 ; } $`           | совпадение ';'                                                                                                                           |
| 90  | `$ } <stmts>`                                                         | `if a < b ) return 1 ; } $`             | `<stmts> → <statement> <stmts>`                                                                                                          |
| 91  | `$ } <stmts> <statement>`                                             | `if a < b ) return 1 ; } $`             | `<statement> → <if> <statement>`                                                                                                         |
| 92  | `$ } <stmts> <statement> <if>`                                        | `if a < b ) return 1 ; } $`             | `<if> → if ( <bool_expression> )`                                                                                                        |
| 93  | `$ } <stmts> <statement> ) <bool_expression> ( if`                    | `if a < b ) return 1 ; } $`             | совпадение 'if'                                                                                                                          |
| 94  | `$ } <stmts> <statement> ) <bool_expression> (`                       | `a < b ) return 1 ; } $`                | Ошибка 8 (пропущен символ: ожидалось: '(' перед 'a') → вставляем '('                                                                     |
| 95  | `$ } <stmts> <statement> ) <bool_expression>`                         | `a < b ) return 1 ; } $`                | `<bool_expression> → id <relop> id`                                                                                                      |
| 96  | `$ } <stmts> <statement> ) id <relop> id`                             | `a < b ) return 1 ; } $`                | совпадение 'a'                                                                                                                           |
| 97  | `$ } <stmts> <statement> ) id <relop>`                                | `< b ) return 1 ; } $`                  | `<relop> → <`                                                                                                                            |
| 98  | `$ } <stmts> <statement> ) id <`                                      | `< b ) return 1 ; } $`                  | совпадение '<'                                                                                                                           |
| 99  | `$ } <stmts> <statement> ) id`                                        | `b ) return 1 ; } $`                    | совпадение 'b'                                                                                                                           |
| 100 | `$ } <stmts> <statement> )`                                           | `) return 1 ; } $`                      | совпадение ')'                                                                                                                           |
| 101 | `$ } <stmts> <statement>`                                             | `return 1 ; } $`                        | `<statement> → <return>`                                                                                                                 |
| 102 | `$ } <stmts> <return>`                                                | `return 1 ; } $`                        | `<return> → return num ;`                                                                                                                |
| 103 | `$ } <stmts> ; num return`                                            | `return 1 ; } $`                        | совпадение 'return'                                                                                                                      |
| 104 | `$ } <stmts> ; num`                                                   | `1 ; } $`                               | совпадение '1'                                                                                                                           |
| 105 | `$ } <stmts> ;`                                                       | `; } $`                                 | совпадение ';'                                                                                                                           |
| 106 | `$ } <stmts>`                                                         | `} $`                                   | `<stmts> → ε`                                                                                                                            |
| 107 | `$ }`                                                                 | `} $`                                   | совпадение '}'                                                                                                                           |
| 108 | `$`                                                                   | `$`                                     | Разбор завершён, синтаксических ошибок: 8                                                                                                |
