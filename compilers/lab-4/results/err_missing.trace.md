# Ход разбора: err_missing.cl

Грамматика: из методички, восстановление: режим паники.

## Исходный текст

```c
// Пропущенные разделители: ';' в заголовке for, ')' в if, ';' после return.
// ожидается: panic=3 phrase=3
int main() {
    for (int i = 0 i < n;)
        if (i != n {
            return 0
        }
}
```

## Ошибки (3)

1. 4:19 — синтаксическая [пропущен символ]: ожидалось: ';' перед 'i'
2. 5:19 — синтаксическая [пропущен символ]: ожидалось: ')' перед '{'
3. 6:21 — синтаксическая [пропущен символ]: ожидалось: ';' перед '}'

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                          | Вход                               | Примечание                                                                  |
|-----|---------------------------------------------------------------|------------------------------------|-----------------------------------------------------------------------------|
| 1   | `$ <program>`                                                 | `int main ( ) { for ( int i = … $` | `<program> → <type> main ( ) { <statement> }`                               |
| 2   | `$ } <statement> { ) ( main <type>`                           | `int main ( ) { for ( int i = … $` | `<type> → int`                                                              |
| 3   | `$ } <statement> { ) ( main int`                              | `int main ( ) { for ( int i = … $` | совпадение 'int'                                                            |
| 4   | `$ } <statement> { ) ( main`                                  | `main ( ) { for ( int i = 0 … $`   | совпадение 'main'                                                           |
| 5   | `$ } <statement> { ) (`                                       | `( ) { for ( int i = 0 i … $`      | совпадение '('                                                              |
| 6   | `$ } <statement> { )`                                         | `) { for ( int i = 0 i < … $`      | совпадение ')'                                                              |
| 7   | `$ } <statement> {`                                           | `{ for ( int i = 0 i < n … $`      | совпадение '{'                                                              |
| 8   | `$ } <statement>`                                             | `for ( int i = 0 i < n ; … $`      | `<statement> → <for> <statement>`                                           |
| 9   | `$ } <statement> <for>`                                       | `for ( int i = 0 i < n ; … $`      | `<for> → for ( <declaration> ; <bool_expression> ; )`                       |
| 10  | `$ } <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( int i = 0 i < n ; … $`      | совпадение 'for'                                                            |
| 11  | `$ } <statement> ) ; <bool_expression> ; <declaration> (`     | `( int i = 0 i < n ; ) … $`        | совпадение '('                                                              |
| 12  | `$ } <statement> ) ; <bool_expression> ; <declaration>`       | `int i = 0 i < n ; ) if … $`       | `<declaration> → <type> id <assign>`                                        |
| 13  | `$ } <statement> ) ; <bool_expression> ; <assign> id <type>`  | `int i = 0 i < n ; ) if … $`       | `<type> → int`                                                              |
| 14  | `$ } <statement> ) ; <bool_expression> ; <assign> id int`     | `int i = 0 i < n ; ) if … $`       | совпадение 'int'                                                            |
| 15  | `$ } <statement> ) ; <bool_expression> ; <assign> id`         | `i = 0 i < n ; ) if ( … $`         | совпадение 'i'                                                              |
| 16  | `$ } <statement> ) ; <bool_expression> ; <assign>`            | `= 0 i < n ; ) if ( i … $`         | `<assign> → = <assign_end>`                                                 |
| 17  | `$ } <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 0 i < n ; ) if ( i … $`         | совпадение '='                                                              |
| 18  | `$ } <statement> ) ; <bool_expression> ; <assign_end>`        | `0 i < n ; ) if ( i != … $`        | `<assign_end> → num`                                                        |
| 19  | `$ } <statement> ) ; <bool_expression> ; num`                 | `0 i < n ; ) if ( i != … $`        | совпадение '0'                                                              |
| 20  | `$ } <statement> ) ; <bool_expression> ;`                     | `i < n ; ) if ( i != n … $`        | Ошибка 1 (пропущен символ: ожидалось: ';' перед 'i') → снимаем ';' со стека |
| 21  | `$ } <statement> ) ; <bool_expression>`                       | `i < n ; ) if ( i != n … $`        | `<bool_expression> → id <relop> id`                                         |
| 22  | `$ } <statement> ) ; id <relop> id`                           | `i < n ; ) if ( i != n … $`        | совпадение 'i'                                                              |
| 23  | `$ } <statement> ) ; id <relop>`                              | `< n ; ) if ( i != n { … $`        | `<relop> → <`                                                               |
| 24  | `$ } <statement> ) ; id <`                                    | `< n ; ) if ( i != n { … $`        | совпадение '<'                                                              |
| 25  | `$ } <statement> ) ; id`                                      | `n ; ) if ( i != n { return … $`   | совпадение 'n'                                                              |
| 26  | `$ } <statement> ) ;`                                         | `; ) if ( i != n { return 0 … $`   | совпадение ';'                                                              |
| 27  | `$ } <statement> )`                                           | `) if ( i != n { return 0 } … $`   | совпадение ')'                                                              |
| 28  | `$ } <statement>`                                             | `if ( i != n { return 0 } } $`     | `<statement> → <if> <statement>`                                            |
| 29  | `$ } <statement> <if>`                                        | `if ( i != n { return 0 } } $`     | `<if> → if ( <bool_expression> )`                                           |
| 30  | `$ } <statement> ) <bool_expression> ( if`                    | `if ( i != n { return 0 } } $`     | совпадение 'if'                                                             |
| 31  | `$ } <statement> ) <bool_expression> (`                       | `( i != n { return 0 } } $`        | совпадение '('                                                              |
| 32  | `$ } <statement> ) <bool_expression>`                         | `i != n { return 0 } } $`          | `<bool_expression> → id <relop> id`                                         |
| 33  | `$ } <statement> ) id <relop> id`                             | `i != n { return 0 } } $`          | совпадение 'i'                                                              |
| 34  | `$ } <statement> ) id <relop>`                                | `!= n { return 0 } } $`            | `<relop> → !=`                                                              |
| 35  | `$ } <statement> ) id !=`                                     | `!= n { return 0 } } $`            | совпадение '!='                                                             |
| 36  | `$ } <statement> ) id`                                        | `n { return 0 } } $`               | совпадение 'n'                                                              |
| 37  | `$ } <statement> )`                                           | `{ return 0 } } $`                 | Ошибка 2 (пропущен символ: ожидалось: ')' перед '{') → снимаем ')' со стека |
| 38  | `$ } <statement>`                                             | `{ return 0 } } $`                 | `<statement> → { <statement> }`                                             |
| 39  | `$ } } <statement> {`                                         | `{ return 0 } } $`                 | совпадение '{'                                                              |
| 40  | `$ } } <statement>`                                           | `return 0 } } $`                   | `<statement> → <return>`                                                    |
| 41  | `$ } } <return>`                                              | `return 0 } } $`                   | `<return> → return num ;`                                                   |
| 42  | `$ } } ; num return`                                          | `return 0 } } $`                   | совпадение 'return'                                                         |
| 43  | `$ } } ; num`                                                 | `0 } } $`                          | совпадение '0'                                                              |
| 44  | `$ } } ;`                                                     | `} } $`                            | Ошибка 3 (пропущен символ: ожидалось: ';' перед '}') → снимаем ';' со стека |
| 45  | `$ } }`                                                       | `} } $`                            | совпадение '}'                                                              |
| 46  | `$ }`                                                         | `} $`                              | совпадение '}'                                                              |
| 47  | `$`                                                           | `$`                                | Разбор завершён, синтаксических ошибок: 3                                   |
