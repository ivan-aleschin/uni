# Ход разбора: ok.cl

Грамматика: из методички, восстановление: режим фразы.

## Исходный текст

```c
// Корректная программа по грамматике из методички. В блоке { } ровно один
// оператор, а for и if «навешиваются» на следующий за ними оператор.
// ожидается: panic=0 phrase=0
int main()
{
    for (int i = 0; i < n;)
        if (limit != i)
            {
                for (bool flag; 10 > i;)
                    if (x == y) return 0;
            }
}
```

## Ошибки (0)

Ошибок нет.

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                            | Вход                                   | Примечание                                            |
|-----|-----------------------------------------------------------------|----------------------------------------|-------------------------------------------------------|
| 1   | `$ <program>`                                                   | `int main ( ) { for ( int i = … $`     | `<program> → <type> main ( ) { <statement> }`         |
| 2   | `$ } <statement> { ) ( main <type>`                             | `int main ( ) { for ( int i = … $`     | `<type> → int`                                        |
| 3   | `$ } <statement> { ) ( main int`                                | `int main ( ) { for ( int i = … $`     | совпадение 'int'                                      |
| 4   | `$ } <statement> { ) ( main`                                    | `main ( ) { for ( int i = 0 … $`       | совпадение 'main'                                     |
| 5   | `$ } <statement> { ) (`                                         | `( ) { for ( int i = 0 ; … $`          | совпадение '('                                        |
| 6   | `$ } <statement> { )`                                           | `) { for ( int i = 0 ; i … $`          | совпадение ')'                                        |
| 7   | `$ } <statement> {`                                             | `{ for ( int i = 0 ; i < … $`          | совпадение '{'                                        |
| 8   | `$ } <statement>`                                               | `for ( int i = 0 ; i < n … $`          | `<statement> → <for> <statement>`                     |
| 9   | `$ } <statement> <for>`                                         | `for ( int i = 0 ; i < n … $`          | `<for> → for ( <declaration> ; <bool_expression> ; )` |
| 10  | `$ } <statement> ) ; <bool_expression> ; <declaration> ( for`   | `for ( int i = 0 ; i < n … $`          | совпадение 'for'                                      |
| 11  | `$ } <statement> ) ; <bool_expression> ; <declaration> (`       | `( int i = 0 ; i < n ; … $`            | совпадение '('                                        |
| 12  | `$ } <statement> ) ; <bool_expression> ; <declaration>`         | `int i = 0 ; i < n ; ) … $`            | `<declaration> → <type> id <assign>`                  |
| 13  | `$ } <statement> ) ; <bool_expression> ; <assign> id <type>`    | `int i = 0 ; i < n ; ) … $`            | `<type> → int`                                        |
| 14  | `$ } <statement> ) ; <bool_expression> ; <assign> id int`       | `int i = 0 ; i < n ; ) … $`            | совпадение 'int'                                      |
| 15  | `$ } <statement> ) ; <bool_expression> ; <assign> id`           | `i = 0 ; i < n ; ) if … $`             | совпадение 'i'                                        |
| 16  | `$ } <statement> ) ; <bool_expression> ; <assign>`              | `= 0 ; i < n ; ) if ( … $`             | `<assign> → = <assign_end>`                           |
| 17  | `$ } <statement> ) ; <bool_expression> ; <assign_end> =`        | `= 0 ; i < n ; ) if ( … $`             | совпадение '='                                        |
| 18  | `$ } <statement> ) ; <bool_expression> ; <assign_end>`          | `0 ; i < n ; ) if ( limit … $`         | `<assign_end> → num`                                  |
| 19  | `$ } <statement> ) ; <bool_expression> ; num`                   | `0 ; i < n ; ) if ( limit … $`         | совпадение '0'                                        |
| 20  | `$ } <statement> ) ; <bool_expression> ;`                       | `; i < n ; ) if ( limit != … $`        | совпадение ';'                                        |
| 21  | `$ } <statement> ) ; <bool_expression>`                         | `i < n ; ) if ( limit != i … $`        | `<bool_expression> → id <relop> id`                   |
| 22  | `$ } <statement> ) ; id <relop> id`                             | `i < n ; ) if ( limit != i … $`        | совпадение 'i'                                        |
| 23  | `$ } <statement> ) ; id <relop>`                                | `< n ; ) if ( limit != i ) … $`        | `<relop> → <`                                         |
| 24  | `$ } <statement> ) ; id <`                                      | `< n ; ) if ( limit != i ) … $`        | совпадение '<'                                        |
| 25  | `$ } <statement> ) ; id`                                        | `n ; ) if ( limit != i ) { … $`        | совпадение 'n'                                        |
| 26  | `$ } <statement> ) ;`                                           | `; ) if ( limit != i ) { for … $`      | совпадение ';'                                        |
| 27  | `$ } <statement> )`                                             | `) if ( limit != i ) { for ( … $`      | совпадение ')'                                        |
| 28  | `$ } <statement>`                                               | `if ( limit != i ) { for ( bool … $`   | `<statement> → <if> <statement>`                      |
| 29  | `$ } <statement> <if>`                                          | `if ( limit != i ) { for ( bool … $`   | `<if> → if ( <bool_expression> )`                     |
| 30  | `$ } <statement> ) <bool_expression> ( if`                      | `if ( limit != i ) { for ( bool … $`   | совпадение 'if'                                       |
| 31  | `$ } <statement> ) <bool_expression> (`                         | `( limit != i ) { for ( bool flag … $` | совпадение '('                                        |
| 32  | `$ } <statement> ) <bool_expression>`                           | `limit != i ) { for ( bool flag ; … $` | `<bool_expression> → id <relop> id`                   |
| 33  | `$ } <statement> ) id <relop> id`                               | `limit != i ) { for ( bool flag ; … $` | совпадение 'limit'                                    |
| 34  | `$ } <statement> ) id <relop>`                                  | `!= i ) { for ( bool flag ; 10 … $`    | `<relop> → !=`                                        |
| 35  | `$ } <statement> ) id !=`                                       | `!= i ) { for ( bool flag ; 10 … $`    | совпадение '!='                                       |
| 36  | `$ } <statement> ) id`                                          | `i ) { for ( bool flag ; 10 > … $`     | совпадение 'i'                                        |
| 37  | `$ } <statement> )`                                             | `) { for ( bool flag ; 10 > i … $`     | совпадение ')'                                        |
| 38  | `$ } <statement>`                                               | `{ for ( bool flag ; 10 > i ; … $`     | `<statement> → { <statement> }`                       |
| 39  | `$ } } <statement> {`                                           | `{ for ( bool flag ; 10 > i ; … $`     | совпадение '{'                                        |
| 40  | `$ } } <statement>`                                             | `for ( bool flag ; 10 > i ; ) … $`     | `<statement> → <for> <statement>`                     |
| 41  | `$ } } <statement> <for>`                                       | `for ( bool flag ; 10 > i ; ) … $`     | `<for> → for ( <declaration> ; <bool_expression> ; )` |
| 42  | `$ } } <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( bool flag ; 10 > i ; ) … $`     | совпадение 'for'                                      |
| 43  | `$ } } <statement> ) ; <bool_expression> ; <declaration> (`     | `( bool flag ; 10 > i ; ) if … $`      | совпадение '('                                        |
| 44  | `$ } } <statement> ) ; <bool_expression> ; <declaration>`       | `bool flag ; 10 > i ; ) if ( … $`      | `<declaration> → <type> id <assign>`                  |
| 45  | `$ } } <statement> ) ; <bool_expression> ; <assign> id <type>`  | `bool flag ; 10 > i ; ) if ( … $`      | `<type> → bool`                                       |
| 46  | `$ } } <statement> ) ; <bool_expression> ; <assign> id bool`    | `bool flag ; 10 > i ; ) if ( … $`      | совпадение 'bool'                                     |
| 47  | `$ } } <statement> ) ; <bool_expression> ; <assign> id`         | `flag ; 10 > i ; ) if ( x … $`         | совпадение 'flag'                                     |
| 48  | `$ } } <statement> ) ; <bool_expression> ; <assign>`            | `; 10 > i ; ) if ( x == … $`           | `<assign> → ε`                                        |
| 49  | `$ } } <statement> ) ; <bool_expression> ;`                     | `; 10 > i ; ) if ( x == … $`           | совпадение ';'                                        |
| 50  | `$ } } <statement> ) ; <bool_expression>`                       | `10 > i ; ) if ( x == y … $`           | `<bool_expression> → num <relop> id`                  |
| 51  | `$ } } <statement> ) ; id <relop> num`                          | `10 > i ; ) if ( x == y … $`           | совпадение '10'                                       |
| 52  | `$ } } <statement> ) ; id <relop>`                              | `> i ; ) if ( x == y ) … $`            | `<relop> → >`                                         |
| 53  | `$ } } <statement> ) ; id >`                                    | `> i ; ) if ( x == y ) … $`            | совпадение '>'                                        |
| 54  | `$ } } <statement> ) ; id`                                      | `i ; ) if ( x == y ) return … $`       | совпадение 'i'                                        |
| 55  | `$ } } <statement> ) ;`                                         | `; ) if ( x == y ) return 0 … $`       | совпадение ';'                                        |
| 56  | `$ } } <statement> )`                                           | `) if ( x == y ) return 0 ; … $`       | совпадение ')'                                        |
| 57  | `$ } } <statement>`                                             | `if ( x == y ) return 0 ; } … $`       | `<statement> → <if> <statement>`                      |
| 58  | `$ } } <statement> <if>`                                        | `if ( x == y ) return 0 ; } … $`       | `<if> → if ( <bool_expression> )`                     |
| 59  | `$ } } <statement> ) <bool_expression> ( if`                    | `if ( x == y ) return 0 ; } … $`       | совпадение 'if'                                       |
| 60  | `$ } } <statement> ) <bool_expression> (`                       | `( x == y ) return 0 ; } } $`          | совпадение '('                                        |
| 61  | `$ } } <statement> ) <bool_expression>`                         | `x == y ) return 0 ; } } $`            | `<bool_expression> → id <relop> id`                   |
| 62  | `$ } } <statement> ) id <relop> id`                             | `x == y ) return 0 ; } } $`            | совпадение 'x'                                        |
| 63  | `$ } } <statement> ) id <relop>`                                | `== y ) return 0 ; } } $`              | `<relop> → ==`                                        |
| 64  | `$ } } <statement> ) id ==`                                     | `== y ) return 0 ; } } $`              | совпадение '=='                                       |
| 65  | `$ } } <statement> ) id`                                        | `y ) return 0 ; } } $`                 | совпадение 'y'                                        |
| 66  | `$ } } <statement> )`                                           | `) return 0 ; } } $`                   | совпадение ')'                                        |
| 67  | `$ } } <statement>`                                             | `return 0 ; } } $`                     | `<statement> → <return>`                              |
| 68  | `$ } } <return>`                                                | `return 0 ; } } $`                     | `<return> → return num ;`                             |
| 69  | `$ } } ; num return`                                            | `return 0 ; } } $`                     | совпадение 'return'                                   |
| 70  | `$ } } ; num`                                                   | `0 ; } } $`                            | совпадение '0'                                        |
| 71  | `$ } } ;`                                                       | `; } } $`                              | совпадение ';'                                        |
| 72  | `$ } }`                                                         | `} } $`                                | совпадение '}'                                        |
| 73  | `$ }`                                                           | `} $`                                  | совпадение '}'                                        |
| 74  | `$`                                                             | `$`                                    | Разбор завершён, ошибок нет                           |
