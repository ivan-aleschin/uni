# Ход разбора: err_multi.cl

Грамматика: из методички, восстановление: режим паники.

## Исходный текст

```c
// Много разных ошибок в одной программе: анализатор должен найти все.
// ожидается: panic=8 phrase=7
int main) {
    for (int = 5; i < 10;)
        if (k = m)
            for (x i = 0; 5 > i;)
                {
                    return x;
                }
}
}
// Что здесь не так (7 настоящих ошибок):
//   3: нет '(' после main;  4: нет имени переменной; справа от '<' число, а нужен идентификатор;
//   5: '=' вместо '==';     6: 'x' — не тип;  8: return допускает только число;
//  11: лишняя '}' после конца main.
```

## Ошибки (8)

1. 3:9 — синтаксическая [пропущен символ]: ожидалось: '(' перед ')'
2. 4:13 — синтаксическая [пропущен символ]: ожидалось: идентификатор перед '='
3. 4:23 — синтаксическая [неожиданный символ]: '10', ожидалось: идентификатор
4. 5:15 — синтаксическая [неожиданный символ]: '=', ожидалось: операция сравнения ('<', '>', '==', '!=')
5. 6:18 — синтаксическая [неполная конструкция]: перед 'x' ожидалось: тип ('int', 'bool', 'void')
6. 6:20 — синтаксическая [неожиданный символ]: 'i', ожидалось: инициализация или конец объявления (';', '=')
7. 8:28 — синтаксическая [неожиданный символ]: 'x', ожидалось: число
8. 11:1 — синтаксическая [текст после конца программы]: '}' после закрывающей '}' функции main

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                          | Вход                               | Примечание                                                                                                                               |
|-----|---------------------------------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | `$ <program>`                                                 | `int main ) { for ( int = 5 ; … $` | `<program> → <type> main ( ) { <statement> }`                                                                                            |
| 2   | `$ } <statement> { ) ( main <type>`                           | `int main ) { for ( int = 5 ; … $` | `<type> → int`                                                                                                                           |
| 3   | `$ } <statement> { ) ( main int`                              | `int main ) { for ( int = 5 ; … $` | совпадение 'int'                                                                                                                         |
| 4   | `$ } <statement> { ) ( main`                                  | `main ) { for ( int = 5 ; i … $`   | совпадение 'main'                                                                                                                        |
| 5   | `$ } <statement> { ) (`                                       | `) { for ( int = 5 ; i < … $`      | Ошибка 1 (пропущен символ: ожидалось: '(' перед ')') → снимаем '(' со стека                                                              |
| 6   | `$ } <statement> { )`                                         | `) { for ( int = 5 ; i < … $`      | совпадение ')'                                                                                                                           |
| 7   | `$ } <statement> {`                                           | `{ for ( int = 5 ; i < 10 … $`     | совпадение '{'                                                                                                                           |
| 8   | `$ } <statement>`                                             | `for ( int = 5 ; i < 10 ; … $`     | `<statement> → <for> <statement>`                                                                                                        |
| 9   | `$ } <statement> <for>`                                       | `for ( int = 5 ; i < 10 ; … $`     | `<for> → for ( <declaration> ; <bool_expression> ; )`                                                                                    |
| 10  | `$ } <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( int = 5 ; i < 10 ; … $`     | совпадение 'for'                                                                                                                         |
| 11  | `$ } <statement> ) ; <bool_expression> ; <declaration> (`     | `( int = 5 ; i < 10 ; ) … $`       | совпадение '('                                                                                                                           |
| 12  | `$ } <statement> ) ; <bool_expression> ; <declaration>`       | `int = 5 ; i < 10 ; ) if … $`      | `<declaration> → <type> id <assign>`                                                                                                     |
| 13  | `$ } <statement> ) ; <bool_expression> ; <assign> id <type>`  | `int = 5 ; i < 10 ; ) if … $`      | `<type> → int`                                                                                                                           |
| 14  | `$ } <statement> ) ; <bool_expression> ; <assign> id int`     | `int = 5 ; i < 10 ; ) if … $`      | совпадение 'int'                                                                                                                         |
| 15  | `$ } <statement> ) ; <bool_expression> ; <assign> id`         | `= 5 ; i < 10 ; ) if ( … $`        | Ошибка 2 (пропущен символ: ожидалось: идентификатор перед '=') → снимаем id со стека                                                     |
| 16  | `$ } <statement> ) ; <bool_expression> ; <assign>`            | `= 5 ; i < 10 ; ) if ( … $`        | `<assign> → = <assign_end>`                                                                                                              |
| 17  | `$ } <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 5 ; i < 10 ; ) if ( … $`        | совпадение '='                                                                                                                           |
| 18  | `$ } <statement> ) ; <bool_expression> ; <assign_end>`        | `5 ; i < 10 ; ) if ( k … $`        | `<assign_end> → num`                                                                                                                     |
| 19  | `$ } <statement> ) ; <bool_expression> ; num`                 | `5 ; i < 10 ; ) if ( k … $`        | совпадение '5'                                                                                                                           |
| 20  | `$ } <statement> ) ; <bool_expression> ;`                     | `; i < 10 ; ) if ( k = … $`        | совпадение ';'                                                                                                                           |
| 21  | `$ } <statement> ) ; <bool_expression>`                       | `i < 10 ; ) if ( k = m … $`        | `<bool_expression> → id <relop> id`                                                                                                      |
| 22  | `$ } <statement> ) ; id <relop> id`                           | `i < 10 ; ) if ( k = m … $`        | совпадение 'i'                                                                                                                           |
| 23  | `$ } <statement> ) ; id <relop>`                              | `< 10 ; ) if ( k = m ) … $`        | `<relop> → <`                                                                                                                            |
| 24  | `$ } <statement> ) ; id <`                                    | `< 10 ; ) if ( k = m ) … $`        | совпадение '<'                                                                                                                           |
| 25  | `$ } <statement> ) ; id`                                      | `10 ; ) if ( k = m ) for … $`      | Ошибка 3 (неожиданный символ: '10', ожидалось: идентификатор) → пропускаем '10'                                                          |
| 26  | `$ } <statement> ) ; id`                                      | `; ) if ( k = m ) for ( … $`       | восстановление → снимаем id со стека                                                                                                     |
| 27  | `$ } <statement> ) ;`                                         | `; ) if ( k = m ) for ( … $`       | совпадение ';'                                                                                                                           |
| 28  | `$ } <statement> )`                                           | `) if ( k = m ) for ( x … $`       | совпадение ')'                                                                                                                           |
| 29  | `$ } <statement>`                                             | `if ( k = m ) for ( x i … $`       | `<statement> → <if> <statement>`                                                                                                         |
| 30  | `$ } <statement> <if>`                                        | `if ( k = m ) for ( x i … $`       | `<if> → if ( <bool_expression> )`                                                                                                        |
| 31  | `$ } <statement> ) <bool_expression> ( if`                    | `if ( k = m ) for ( x i … $`       | совпадение 'if'                                                                                                                          |
| 32  | `$ } <statement> ) <bool_expression> (`                       | `( k = m ) for ( x i = … $`        | совпадение '('                                                                                                                           |
| 33  | `$ } <statement> ) <bool_expression>`                         | `k = m ) for ( x i = 0 … $`        | `<bool_expression> → id <relop> id`                                                                                                      |
| 34  | `$ } <statement> ) id <relop> id`                             | `k = m ) for ( x i = 0 … $`        | совпадение 'k'                                                                                                                           |
| 35  | `$ } <statement> ) id <relop>`                                | `= m ) for ( x i = 0 ; … $`        | Ошибка 4 (неожиданный символ: '=', ожидалось: операция сравнения ('<', '>', '==', '!=')), `M[<relop>, =]` пусто → пропускаем '='         |
| 36  | `$ } <statement> ) id <relop>`                                | `m ) for ( x i = 0 ; 5 … $`        | восстановление, `M[<relop>, id]` = synch → `<relop>` снимается со стека                                                                  |
| 37  | `$ } <statement> ) id`                                        | `m ) for ( x i = 0 ; 5 … $`        | совпадение 'm'                                                                                                                           |
| 38  | `$ } <statement> )`                                           | `) for ( x i = 0 ; 5 > … $`        | совпадение ')'                                                                                                                           |
| 39  | `$ } <statement>`                                             | `for ( x i = 0 ; 5 > i … $`        | `<statement> → <for> <statement>`                                                                                                        |
| 40  | `$ } <statement> <for>`                                       | `for ( x i = 0 ; 5 > i … $`        | `<for> → for ( <declaration> ; <bool_expression> ; )`                                                                                    |
| 41  | `$ } <statement> ) ; <bool_expression> ; <declaration> ( for` | `for ( x i = 0 ; 5 > i … $`        | совпадение 'for'                                                                                                                         |
| 42  | `$ } <statement> ) ; <bool_expression> ; <declaration> (`     | `( x i = 0 ; 5 > i ; … $`          | совпадение '('                                                                                                                           |
| 43  | `$ } <statement> ) ; <bool_expression> ; <declaration>`       | `x i = 0 ; 5 > i ; ) … $`          | `M[<declaration>, id]` пусто, у `<declaration>` одна продукция — раскрываем её по умолчанию: `<declaration> → <type> id <assign>`        |
| 44  | `$ } <statement> ) ; <bool_expression> ; <assign> id <type>`  | `x i = 0 ; 5 > i ; ) … $`          | Ошибка 5 (неполная конструкция: перед 'x' ожидалось: тип ('int', 'bool', 'void')), `M[<type>, id]` = synch → `<type>` снимается со стека |
| 45  | `$ } <statement> ) ; <bool_expression> ; <assign> id`         | `x i = 0 ; 5 > i ; ) … $`          | совпадение 'x'                                                                                                                           |
| 46  | `$ } <statement> ) ; <bool_expression> ; <assign>`            | `i = 0 ; 5 > i ; ) { … $`          | Ошибка 6 (неожиданный символ: 'i', ожидалось: инициализация или конец объявления (';', '=')), `M[<assign>, id]` пусто → пропускаем 'i'   |
| 47  | `$ } <statement> ) ; <bool_expression> ; <assign>`            | `= 0 ; 5 > i ; ) { return … $`     | `<assign> → = <assign_end>`                                                                                                              |
| 48  | `$ } <statement> ) ; <bool_expression> ; <assign_end> =`      | `= 0 ; 5 > i ; ) { return … $`     | совпадение '='                                                                                                                           |
| 49  | `$ } <statement> ) ; <bool_expression> ; <assign_end>`        | `0 ; 5 > i ; ) { return x … $`     | `<assign_end> → num`                                                                                                                     |
| 50  | `$ } <statement> ) ; <bool_expression> ; num`                 | `0 ; 5 > i ; ) { return x … $`     | совпадение '0'                                                                                                                           |
| 51  | `$ } <statement> ) ; <bool_expression> ;`                     | `; 5 > i ; ) { return x ; … $`     | совпадение ';'                                                                                                                           |
| 52  | `$ } <statement> ) ; <bool_expression>`                       | `5 > i ; ) { return x ; } … $`     | `<bool_expression> → num <relop> id`                                                                                                     |
| 53  | `$ } <statement> ) ; id <relop> num`                          | `5 > i ; ) { return x ; } … $`     | совпадение '5'                                                                                                                           |
| 54  | `$ } <statement> ) ; id <relop>`                              | `> i ; ) { return x ; } } … $`     | `<relop> → >`                                                                                                                            |
| 55  | `$ } <statement> ) ; id >`                                    | `> i ; ) { return x ; } } … $`     | совпадение '>'                                                                                                                           |
| 56  | `$ } <statement> ) ; id`                                      | `i ; ) { return x ; } } } $`       | совпадение 'i'                                                                                                                           |
| 57  | `$ } <statement> ) ;`                                         | `; ) { return x ; } } } $`         | совпадение ';'                                                                                                                           |
| 58  | `$ } <statement> )`                                           | `) { return x ; } } } $`           | совпадение ')'                                                                                                                           |
| 59  | `$ } <statement>`                                             | `{ return x ; } } } $`             | `<statement> → { <statement> }`                                                                                                          |
| 60  | `$ } } <statement> {`                                         | `{ return x ; } } } $`             | совпадение '{'                                                                                                                           |
| 61  | `$ } } <statement>`                                           | `return x ; } } } $`               | `<statement> → <return>`                                                                                                                 |
| 62  | `$ } } <return>`                                              | `return x ; } } } $`               | `<return> → return num ;`                                                                                                                |
| 63  | `$ } } ; num return`                                          | `return x ; } } } $`               | совпадение 'return'                                                                                                                      |
| 64  | `$ } } ; num`                                                 | `x ; } } } $`                      | Ошибка 7 (неожиданный символ: 'x', ожидалось: число) → пропускаем 'x'                                                                    |
| 65  | `$ } } ; num`                                                 | `; } } } $`                        | восстановление → снимаем num со стека                                                                                                    |
| 66  | `$ } } ;`                                                     | `; } } } $`                        | совпадение ';'                                                                                                                           |
| 67  | `$ } }`                                                       | `} } } $`                          | совпадение '}'                                                                                                                           |
| 68  | `$ }`                                                         | `} } $`                            | совпадение '}'                                                                                                                           |
| 69  | `$`                                                           | `} $`                              | Ошибка 8 (текст после конца программы: '}' после закрывающей '}' функции main) → пропускаем '}'                                          |
| 70  | `$`                                                           | `$`                                | Разбор завершён, синтаксических ошибок: 8                                                                                                |
