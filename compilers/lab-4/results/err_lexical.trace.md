# Ход разбора: err_lexical.cl

Грамматика: из методички, восстановление: режим паники.

## Исходный текст

```c
// Лексические ошибки: цифры в идентификаторе, буквы в числе, '<=', чужой символ.
// ожидается: panic=6 phrase=6
int main() {
    for (int x1 = 12ab; x1 <= n;)
        if (a @ b) return 0;
}
```

## Ошибки (6)

- 4:14 — лексическая [неверный идентификатор]: 'x1': по грамматике C-light идентификатор состоит только из букв и '_', цифры не допускаются
- 4:19 — лексическая [неверное число]: '12ab': число может содержать только цифры
- 4:25 — лексическая [неверный идентификатор]: 'x1': по грамматике C-light идентификатор состоит только из букв и '_', цифры не допускаются
- 4:28 — лексическая [неподдерживаемая операция]: операции '<=' нет в C-light (есть только <, >, ==, !=); считаем, что написано '<'
- 5:15 — лексическая [недопустимый символ]: символ '@' не входит в алфавит C-light, пропущен

1. 5:17 — синтаксическая [неполная конструкция]: перед 'b' ожидалось: операция сравнения ('<', '>', '==', '!=')

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                          | Вход                                 | Примечание                                                                                                                                               |
|-----|---------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | `$ <program>`                                                 | `int main ( ) { for ( int x1 = … $`  | `<program> → <type> main ( ) { <statement> }`                                                                                                            |
| 2   | `$ } <statement> { ) ( main <type>`                           | `int main ( ) { for ( int x1 = … $`  | `<type> → int`                                                                                                                                           |
| 3   | `$ } <statement> { ) ( main int`                              | `int main ( ) { for ( int x1 = … $`  | совпадение 'int'                                                                                                                                         |
| 4   | `$ } <statement> { ) ( main`                                  | `main ( ) { for ( int x1 = 12ab … $` | совпадение 'main'                                                                                                                                        |
| 5   | `$ } <statement> { ) (`                                       | `( ) { for ( int x1 = 12ab ; … $`    | совпадение '('                                                                                                                                           |
| 6   | `$ } <statement> { )`                                         | `) { for ( int x1 = 12ab ; x1 … $`   | совпадение ')'                                                                                                                                           |
| 7   | `$ } <statement> {`                                           | `{ for ( int x1 = 12ab ; x1 < … $`   | совпадение '{'                                                                                                                                           |
| 8   | `$ } <statement>`                                             | `for ( int x1 = 12ab ; x1 < n … $`   | `<statement> → <for> <statement>`                                                                                                                        |
| 9   | `$ } <statement> <for>`                                       | `for ( int x1 = 12ab ; x1 < n … $`   | `<for> → for ( <declaration> ; <bool_expression> ; )`                                                                                                    |
| 10  | `$ } <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( int x1 = 12ab ; x1 < n … $`   | совпадение 'for'                                                                                                                                         |
| 11  | `$ } <statement> ) ; <bool_expression> ; <declaration> (`     | `( int x1 = 12ab ; x1 < n ; … $`     | совпадение '('                                                                                                                                           |
| 12  | `$ } <statement> ) ; <bool_expression> ; <declaration>`       | `int x1 = 12ab ; x1 < n ; ) … $`     | `<declaration> → <type> id <assign>`                                                                                                                     |
| 13  | `$ } <statement> ) ; <bool_expression> ; <assign> id <type>`  | `int x1 = 12ab ; x1 < n ; ) … $`     | `<type> → int`                                                                                                                                           |
| 14  | `$ } <statement> ) ; <bool_expression> ; <assign> id int`     | `int x1 = 12ab ; x1 < n ; ) … $`     | совпадение 'int'                                                                                                                                         |
| 15  | `$ } <statement> ) ; <bool_expression> ; <assign> id`         | `x1 = 12ab ; x1 < n ; ) if … $`      | совпадение 'x1'                                                                                                                                          |
| 16  | `$ } <statement> ) ; <bool_expression> ; <assign>`            | `= 12ab ; x1 < n ; ) if ( … $`       | `<assign> → = <assign_end>`                                                                                                                              |
| 17  | `$ } <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 12ab ; x1 < n ; ) if ( … $`       | совпадение '='                                                                                                                                           |
| 18  | `$ } <statement> ) ; <bool_expression> ; <assign_end>`        | `12ab ; x1 < n ; ) if ( a … $`       | `<assign_end> → num`                                                                                                                                     |
| 19  | `$ } <statement> ) ; <bool_expression> ; num`                 | `12ab ; x1 < n ; ) if ( a … $`       | совпадение '12ab'                                                                                                                                        |
| 20  | `$ } <statement> ) ; <bool_expression> ;`                     | `; x1 < n ; ) if ( a b … $`          | совпадение ';'                                                                                                                                           |
| 21  | `$ } <statement> ) ; <bool_expression>`                       | `x1 < n ; ) if ( a b ) … $`          | `<bool_expression> → id <relop> id`                                                                                                                      |
| 22  | `$ } <statement> ) ; id <relop> id`                           | `x1 < n ; ) if ( a b ) … $`          | совпадение 'x1'                                                                                                                                          |
| 23  | `$ } <statement> ) ; id <relop>`                              | `< n ; ) if ( a b ) return … $`      | `<relop> → <`                                                                                                                                            |
| 24  | `$ } <statement> ) ; id <`                                    | `< n ; ) if ( a b ) return … $`      | совпадение '<'                                                                                                                                           |
| 25  | `$ } <statement> ) ; id`                                      | `n ; ) if ( a b ) return 0 … $`      | совпадение 'n'                                                                                                                                           |
| 26  | `$ } <statement> ) ;`                                         | `; ) if ( a b ) return 0 ; … $`      | совпадение ';'                                                                                                                                           |
| 27  | `$ } <statement> )`                                           | `) if ( a b ) return 0 ; } $`        | совпадение ')'                                                                                                                                           |
| 28  | `$ } <statement>`                                             | `if ( a b ) return 0 ; } $`          | `<statement> → <if> <statement>`                                                                                                                         |
| 29  | `$ } <statement> <if>`                                        | `if ( a b ) return 0 ; } $`          | `<if> → if ( <bool_expression> )`                                                                                                                        |
| 30  | `$ } <statement> ) <bool_expression> ( if`                    | `if ( a b ) return 0 ; } $`          | совпадение 'if'                                                                                                                                          |
| 31  | `$ } <statement> ) <bool_expression> (`                       | `( a b ) return 0 ; } $`             | совпадение '('                                                                                                                                           |
| 32  | `$ } <statement> ) <bool_expression>`                         | `a b ) return 0 ; } $`               | `<bool_expression> → id <relop> id`                                                                                                                      |
| 33  | `$ } <statement> ) id <relop> id`                             | `a b ) return 0 ; } $`               | совпадение 'a'                                                                                                                                           |
| 34  | `$ } <statement> ) id <relop>`                                | `b ) return 0 ; } $`                 | Ошибка 1 (неполная конструкция: перед 'b' ожидалось: операция сравнения ('<', '>', '==', '!=')), `M[<relop>, id]` = synch → `<relop>` снимается со стека |
| 35  | `$ } <statement> ) id`                                        | `b ) return 0 ; } $`                 | совпадение 'b'                                                                                                                                           |
| 36  | `$ } <statement> )`                                           | `) return 0 ; } $`                   | совпадение ')'                                                                                                                                           |
| 37  | `$ } <statement>`                                             | `return 0 ; } $`                     | `<statement> → <return>`                                                                                                                                 |
| 38  | `$ } <return>`                                                | `return 0 ; } $`                     | `<return> → return num ;`                                                                                                                                |
| 39  | `$ } ; num return`                                            | `return 0 ; } $`                     | совпадение 'return'                                                                                                                                      |
| 40  | `$ } ; num`                                                   | `0 ; } $`                            | совпадение '0'                                                                                                                                           |
| 41  | `$ } ;`                                                       | `; } $`                              | совпадение ';'                                                                                                                                           |
| 42  | `$ }`                                                         | `} $`                                | совпадение '}'                                                                                                                                           |
| 43  | `$`                                                           | `$`                                  | Разбор завершён, синтаксических ошибок: 1                                                                                                                |
