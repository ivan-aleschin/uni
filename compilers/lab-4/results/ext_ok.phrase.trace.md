# Ход разбора: ext_ok.cl

Грамматика: расширенная (--ext), восстановление: режим фразы.

## Исходный текст

```c
// Расширенная грамматика: в блоке последовательность операторов, ';' — пустой оператор.
// флаги: --ext
// ожидается: panic=0 phrase=0
int main() {
    int a = 1;
    bool flag;
    for (int i = 0; i < n;) {
        if (i == a) return 0;
        int tmp = i;
    }
    ;
    return 1;
}
```

## Ошибки (0)

Ошибок нет.

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                                  | Вход                                | Примечание                                            |
|-----|-----------------------------------------------------------------------|-------------------------------------|-------------------------------------------------------|
| 1   | `$ <program>`                                                         | `int main ( ) { int a = 1 ; … $`    | `<program> → <type> main ( ) { <stmts> }`             |
| 2   | `$ } <stmts> { ) ( main <type>`                                       | `int main ( ) { int a = 1 ; … $`    | `<type> → int`                                        |
| 3   | `$ } <stmts> { ) ( main int`                                          | `int main ( ) { int a = 1 ; … $`    | совпадение 'int'                                      |
| 4   | `$ } <stmts> { ) ( main`                                              | `main ( ) { int a = 1 ; bool … $`   | совпадение 'main'                                     |
| 5   | `$ } <stmts> { ) (`                                                   | `( ) { int a = 1 ; bool flag … $`   | совпадение '('                                        |
| 6   | `$ } <stmts> { )`                                                     | `) { int a = 1 ; bool flag ; … $`   | совпадение ')'                                        |
| 7   | `$ } <stmts> {`                                                       | `{ int a = 1 ; bool flag ; for … $` | совпадение '{'                                        |
| 8   | `$ } <stmts>`                                                         | `int a = 1 ; bool flag ; for ( … $` | `<stmts> → <statement> <stmts>`                       |
| 9   | `$ } <stmts> <statement>`                                             | `int a = 1 ; bool flag ; for ( … $` | `<statement> → <declaration> ;`                       |
| 10  | `$ } <stmts> ; <declaration>`                                         | `int a = 1 ; bool flag ; for ( … $` | `<declaration> → <type> id <assign>`                  |
| 11  | `$ } <stmts> ; <assign> id <type>`                                    | `int a = 1 ; bool flag ; for ( … $` | `<type> → int`                                        |
| 12  | `$ } <stmts> ; <assign> id int`                                       | `int a = 1 ; bool flag ; for ( … $` | совпадение 'int'                                      |
| 13  | `$ } <stmts> ; <assign> id`                                           | `a = 1 ; bool flag ; for ( int … $` | совпадение 'a'                                        |
| 14  | `$ } <stmts> ; <assign>`                                              | `= 1 ; bool flag ; for ( int i … $` | `<assign> → = <assign_end>`                           |
| 15  | `$ } <stmts> ; <assign_end> =`                                        | `= 1 ; bool flag ; for ( int i … $` | совпадение '='                                        |
| 16  | `$ } <stmts> ; <assign_end>`                                          | `1 ; bool flag ; for ( int i = … $` | `<assign_end> → num`                                  |
| 17  | `$ } <stmts> ; num`                                                   | `1 ; bool flag ; for ( int i = … $` | совпадение '1'                                        |
| 18  | `$ } <stmts> ;`                                                       | `; bool flag ; for ( int i = 0 … $` | совпадение ';'                                        |
| 19  | `$ } <stmts>`                                                         | `bool flag ; for ( int i = 0 ; … $` | `<stmts> → <statement> <stmts>`                       |
| 20  | `$ } <stmts> <statement>`                                             | `bool flag ; for ( int i = 0 ; … $` | `<statement> → <declaration> ;`                       |
| 21  | `$ } <stmts> ; <declaration>`                                         | `bool flag ; for ( int i = 0 ; … $` | `<declaration> → <type> id <assign>`                  |
| 22  | `$ } <stmts> ; <assign> id <type>`                                    | `bool flag ; for ( int i = 0 ; … $` | `<type> → bool`                                       |
| 23  | `$ } <stmts> ; <assign> id bool`                                      | `bool flag ; for ( int i = 0 ; … $` | совпадение 'bool'                                     |
| 24  | `$ } <stmts> ; <assign> id`                                           | `flag ; for ( int i = 0 ; i … $`    | совпадение 'flag'                                     |
| 25  | `$ } <stmts> ; <assign>`                                              | `; for ( int i = 0 ; i < … $`       | `<assign> → ε`                                        |
| 26  | `$ } <stmts> ;`                                                       | `; for ( int i = 0 ; i < … $`       | совпадение ';'                                        |
| 27  | `$ } <stmts>`                                                         | `for ( int i = 0 ; i < n … $`       | `<stmts> → <statement> <stmts>`                       |
| 28  | `$ } <stmts> <statement>`                                             | `for ( int i = 0 ; i < n … $`       | `<statement> → <for> <statement>`                     |
| 29  | `$ } <stmts> <statement> <for>`                                       | `for ( int i = 0 ; i < n … $`       | `<for> → for ( <declaration> ; <bool_expression> ; )` |
| 30  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( int i = 0 ; i < n … $`       | совпадение 'for'                                      |
| 31  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> (`     | `( int i = 0 ; i < n ; … $`         | совпадение '('                                        |
| 32  | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration>`       | `int i = 0 ; i < n ; ) … $`         | `<declaration> → <type> id <assign>`                  |
| 33  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id <type>`  | `int i = 0 ; i < n ; ) … $`         | `<type> → int`                                        |
| 34  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id int`     | `int i = 0 ; i < n ; ) … $`         | совпадение 'int'                                      |
| 35  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign> id`         | `i = 0 ; i < n ; ) { … $`           | совпадение 'i'                                        |
| 36  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign>`            | `= 0 ; i < n ; ) { if … $`          | `<assign> → = <assign_end>`                           |
| 37  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 0 ; i < n ; ) { if … $`          | совпадение '='                                        |
| 38  | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end>`        | `0 ; i < n ; ) { if ( … $`          | `<assign_end> → num`                                  |
| 39  | `$ } <stmts> <statement> ) ; <bool_expression> ; num`                 | `0 ; i < n ; ) { if ( … $`          | совпадение '0'                                        |
| 40  | `$ } <stmts> <statement> ) ; <bool_expression> ;`                     | `; i < n ; ) { if ( i … $`          | совпадение ';'                                        |
| 41  | `$ } <stmts> <statement> ) ; <bool_expression>`                       | `i < n ; ) { if ( i == … $`         | `<bool_expression> → id <relop> id`                   |
| 42  | `$ } <stmts> <statement> ) ; id <relop> id`                           | `i < n ; ) { if ( i == … $`         | совпадение 'i'                                        |
| 43  | `$ } <stmts> <statement> ) ; id <relop>`                              | `< n ; ) { if ( i == a … $`         | `<relop> → <`                                         |
| 44  | `$ } <stmts> <statement> ) ; id <`                                    | `< n ; ) { if ( i == a … $`         | совпадение '<'                                        |
| 45  | `$ } <stmts> <statement> ) ; id`                                      | `n ; ) { if ( i == a ) … $`         | совпадение 'n'                                        |
| 46  | `$ } <stmts> <statement> ) ;`                                         | `; ) { if ( i == a ) return … $`    | совпадение ';'                                        |
| 47  | `$ } <stmts> <statement> )`                                           | `) { if ( i == a ) return 0 … $`    | совпадение ')'                                        |
| 48  | `$ } <stmts> <statement>`                                             | `{ if ( i == a ) return 0 ; … $`    | `<statement> → { <stmts> }`                           |
| 49  | `$ } <stmts> } <stmts> {`                                             | `{ if ( i == a ) return 0 ; … $`    | совпадение '{'                                        |
| 50  | `$ } <stmts> } <stmts>`                                               | `if ( i == a ) return 0 ; int … $`  | `<stmts> → <statement> <stmts>`                       |
| 51  | `$ } <stmts> } <stmts> <statement>`                                   | `if ( i == a ) return 0 ; int … $`  | `<statement> → <if> <statement>`                      |
| 52  | `$ } <stmts> } <stmts> <statement> <if>`                              | `if ( i == a ) return 0 ; int … $`  | `<if> → if ( <bool_expression> )`                     |
| 53  | `$ } <stmts> } <stmts> <statement> ) <bool_expression> ( if`          | `if ( i == a ) return 0 ; int … $`  | совпадение 'if'                                       |
| 54  | `$ } <stmts> } <stmts> <statement> ) <bool_expression> (`             | `( i == a ) return 0 ; int tmp … $` | совпадение '('                                        |
| 55  | `$ } <stmts> } <stmts> <statement> ) <bool_expression>`               | `i == a ) return 0 ; int tmp = … $` | `<bool_expression> → id <relop> id`                   |
| 56  | `$ } <stmts> } <stmts> <statement> ) id <relop> id`                   | `i == a ) return 0 ; int tmp = … $` | совпадение 'i'                                        |
| 57  | `$ } <stmts> } <stmts> <statement> ) id <relop>`                      | `== a ) return 0 ; int tmp = i … $` | `<relop> → ==`                                        |
| 58  | `$ } <stmts> } <stmts> <statement> ) id ==`                           | `== a ) return 0 ; int tmp = i … $` | совпадение '=='                                       |
| 59  | `$ } <stmts> } <stmts> <statement> ) id`                              | `a ) return 0 ; int tmp = i ; … $`  | совпадение 'a'                                        |
| 60  | `$ } <stmts> } <stmts> <statement> )`                                 | `) return 0 ; int tmp = i ; } … $`  | совпадение ')'                                        |
| 61  | `$ } <stmts> } <stmts> <statement>`                                   | `return 0 ; int tmp = i ; } ; … $`  | `<statement> → <return>`                              |
| 62  | `$ } <stmts> } <stmts> <return>`                                      | `return 0 ; int tmp = i ; } ; … $`  | `<return> → return num ;`                             |
| 63  | `$ } <stmts> } <stmts> ; num return`                                  | `return 0 ; int tmp = i ; } ; … $`  | совпадение 'return'                                   |
| 64  | `$ } <stmts> } <stmts> ; num`                                         | `0 ; int tmp = i ; } ; return … $`  | совпадение '0'                                        |
| 65  | `$ } <stmts> } <stmts> ;`                                             | `; int tmp = i ; } ; return 1 … $`  | совпадение ';'                                        |
| 66  | `$ } <stmts> } <stmts>`                                               | `int tmp = i ; } ; return 1 ; … $`  | `<stmts> → <statement> <stmts>`                       |
| 67  | `$ } <stmts> } <stmts> <statement>`                                   | `int tmp = i ; } ; return 1 ; … $`  | `<statement> → <declaration> ;`                       |
| 68  | `$ } <stmts> } <stmts> ; <declaration>`                               | `int tmp = i ; } ; return 1 ; … $`  | `<declaration> → <type> id <assign>`                  |
| 69  | `$ } <stmts> } <stmts> ; <assign> id <type>`                          | `int tmp = i ; } ; return 1 ; … $`  | `<type> → int`                                        |
| 70  | `$ } <stmts> } <stmts> ; <assign> id int`                             | `int tmp = i ; } ; return 1 ; … $`  | совпадение 'int'                                      |
| 71  | `$ } <stmts> } <stmts> ; <assign> id`                                 | `tmp = i ; } ; return 1 ; } $`      | совпадение 'tmp'                                      |
| 72  | `$ } <stmts> } <stmts> ; <assign>`                                    | `= i ; } ; return 1 ; } $`          | `<assign> → = <assign_end>`                           |
| 73  | `$ } <stmts> } <stmts> ; <assign_end> =`                              | `= i ; } ; return 1 ; } $`          | совпадение '='                                        |
| 74  | `$ } <stmts> } <stmts> ; <assign_end>`                                | `i ; } ; return 1 ; } $`            | `<assign_end> → id`                                   |
| 75  | `$ } <stmts> } <stmts> ; id`                                          | `i ; } ; return 1 ; } $`            | совпадение 'i'                                        |
| 76  | `$ } <stmts> } <stmts> ;`                                             | `; } ; return 1 ; } $`              | совпадение ';'                                        |
| 77  | `$ } <stmts> } <stmts>`                                               | `} ; return 1 ; } $`                | `<stmts> → ε`                                         |
| 78  | `$ } <stmts> }`                                                       | `} ; return 1 ; } $`                | совпадение '}'                                        |
| 79  | `$ } <stmts>`                                                         | `; return 1 ; } $`                  | `<stmts> → <statement> <stmts>`                       |
| 80  | `$ } <stmts> <statement>`                                             | `; return 1 ; } $`                  | `<statement> → ;`                                     |
| 81  | `$ } <stmts> ;`                                                       | `; return 1 ; } $`                  | совпадение ';'                                        |
| 82  | `$ } <stmts>`                                                         | `return 1 ; } $`                    | `<stmts> → <statement> <stmts>`                       |
| 83  | `$ } <stmts> <statement>`                                             | `return 1 ; } $`                    | `<statement> → <return>`                              |
| 84  | `$ } <stmts> <return>`                                                | `return 1 ; } $`                    | `<return> → return num ;`                             |
| 85  | `$ } <stmts> ; num return`                                            | `return 1 ; } $`                    | совпадение 'return'                                   |
| 86  | `$ } <stmts> ; num`                                                   | `1 ; } $`                           | совпадение '1'                                        |
| 87  | `$ } <stmts> ;`                                                       | `; } $`                             | совпадение ';'                                        |
| 88  | `$ } <stmts>`                                                         | `} $`                               | `<stmts> → ε`                                         |
| 89  | `$ }`                                                                 | `} $`                               | совпадение '}'                                        |
| 90  | `$`                                                                   | `$`                                 | Разбор завершён, ошибок нет                           |
