# Ход разбора: arr_semantic.cl

Грамматика: с массивами (--arrays), восстановление: режим паники.

## Исходный текст

```c
// Семантические ошибки массивов: синтаксически всё верно.
// флаги: --arrays
// ожидается: panic=6 phrase=6
int main() {
    int a[0];
    int b[2] = {1, 2, 3};
    int c[];
    int d[3] = {1, 2, 3};
    int x = d[3];
    int y = 5;
    y[0] = 1;
    int z = d;
    return 0;
}
// Ошибки: 5 — размер 0, 6 — три значения в массиве из двух, 7 — нет ни размера,
// ни инициализации, 9 — индекс 3 вне 0..2, 11 — y не массив, 12 — массив без индекса.
```

## Ошибки (6)


- 5:11 — семантическая [неверный размер массива]: размер массива 'a' должен быть больше нуля
- 6:14 — семантическая [слишком много инициализаторов]: размер массива 'b' — 2, а значений в списке — 3
- 7:9 — семантическая [не указан размер массива]: у массива 'c' нет ни размера, ни списка инициализации
- 9:15 — семантическая [индекс за границами массива]: 'd[3]': допустимые индексы массива 'd' — от 0 до 2
- 11:5 — семантическая [индексация не массива]: 'y' объявлена как переменная, а не массив
- 12:13 — семантическая [массив без индекса]: 'd' — массив, к нему можно обращаться только по индексу: d[i]

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                           | Вход                             | Примечание                                  |
|-----|------------------------------------------------|----------------------------------|---------------------------------------------|
| 1   | `$ <program>`                                  | `int main ( ) { int a [ 0 ] … $` | `<program> → <type> main ( ) { <stmts> }`   |
| 2   | `$ } <stmts> { ) ( main <type>`                | `int main ( ) { int a [ 0 ] … $` | `<type> → int`                              |
| 3   | `$ } <stmts> { ) ( main int`                   | `int main ( ) { int a [ 0 ] … $` | совпадение 'int'                            |
| 4   | `$ } <stmts> { ) ( main`                       | `main ( ) { int a [ 0 ] ; … $`   | совпадение 'main'                           |
| 5   | `$ } <stmts> { ) (`                            | `( ) { int a [ 0 ] ; int … $`    | совпадение '('                              |
| 6   | `$ } <stmts> { )`                              | `) { int a [ 0 ] ; int b … $`    | совпадение ')'                              |
| 7   | `$ } <stmts> {`                                | `{ int a [ 0 ] ; int b [ … $`    | совпадение '{'                              |
| 8   | `$ } <stmts>`                                  | `int a [ 0 ] ; int b [ 2 … $`    | `<stmts> → <statement> <stmts>`             |
| 9   | `$ } <stmts> <statement>`                      | `int a [ 0 ] ; int b [ 2 … $`    | `<statement> → <declaration> ;`             |
| 10  | `$ } <stmts> ; <declaration>`                  | `int a [ 0 ] ; int b [ 2 … $`    | `<declaration> → <type> id <decl_tail>`     |
| 11  | `$ } <stmts> ; <decl_tail> id <type>`          | `int a [ 0 ] ; int b [ 2 … $`    | `<type> → int`                              |
| 12  | `$ } <stmts> ; <decl_tail> id int`             | `int a [ 0 ] ; int b [ 2 … $`    | совпадение 'int'                            |
| 13  | `$ } <stmts> ; <decl_tail> id`                 | `a [ 0 ] ; int b [ 2 ] … $`      | совпадение 'a'                              |
| 14  | `$ } <stmts> ; <decl_tail>`                    | `[ 0 ] ; int b [ 2 ] = … $`      | `<decl_tail> → [ <size> ] <array_init>`     |
| 15  | `$ } <stmts> ; <array_init> ] <size> [`        | `[ 0 ] ; int b [ 2 ] = … $`      | совпадение '['                              |
| 16  | `$ } <stmts> ; <array_init> ] <size>`          | `0 ] ; int b [ 2 ] = { … $`      | `<size> → num`                              |
| 17  | `$ } <stmts> ; <array_init> ] num`             | `0 ] ; int b [ 2 ] = { … $`      | совпадение '0'                              |
| 18  | `$ } <stmts> ; <array_init> ]`                 | `] ; int b [ 2 ] = { 1 … $`      | совпадение ']'                              |
| 19  | `$ } <stmts> ; <array_init>`                   | `; int b [ 2 ] = { 1 , … $`      | `<array_init> → ε`                          |
| 20  | `$ } <stmts> ;`                                | `; int b [ 2 ] = { 1 , … $`      | совпадение ';'                              |
| 21  | `$ } <stmts>`                                  | `int b [ 2 ] = { 1 , 2 … $`      | `<stmts> → <statement> <stmts>`             |
| 22  | `$ } <stmts> <statement>`                      | `int b [ 2 ] = { 1 , 2 … $`      | `<statement> → <declaration> ;`             |
| 23  | `$ } <stmts> ; <declaration>`                  | `int b [ 2 ] = { 1 , 2 … $`      | `<declaration> → <type> id <decl_tail>`     |
| 24  | `$ } <stmts> ; <decl_tail> id <type>`          | `int b [ 2 ] = { 1 , 2 … $`      | `<type> → int`                              |
| 25  | `$ } <stmts> ; <decl_tail> id int`             | `int b [ 2 ] = { 1 , 2 … $`      | совпадение 'int'                            |
| 26  | `$ } <stmts> ; <decl_tail> id`                 | `b [ 2 ] = { 1 , 2 , … $`        | совпадение 'b'                              |
| 27  | `$ } <stmts> ; <decl_tail>`                    | `[ 2 ] = { 1 , 2 , 3 … $`        | `<decl_tail> → [ <size> ] <array_init>`     |
| 28  | `$ } <stmts> ; <array_init> ] <size> [`        | `[ 2 ] = { 1 , 2 , 3 … $`        | совпадение '['                              |
| 29  | `$ } <stmts> ; <array_init> ] <size>`          | `2 ] = { 1 , 2 , 3 } … $`        | `<size> → num`                              |
| 30  | `$ } <stmts> ; <array_init> ] num`             | `2 ] = { 1 , 2 , 3 } … $`        | совпадение '2'                              |
| 31  | `$ } <stmts> ; <array_init> ]`                 | `] = { 1 , 2 , 3 } ; … $`        | совпадение ']'                              |
| 32  | `$ } <stmts> ; <array_init>`                   | `= { 1 , 2 , 3 } ; int … $`      | `<array_init> → = { <init_list> }`          |
| 33  | `$ } <stmts> ; } <init_list> { =`              | `= { 1 , 2 , 3 } ; int … $`      | совпадение '='                              |
| 34  | `$ } <stmts> ; } <init_list> {`                | `{ 1 , 2 , 3 } ; int c … $`      | совпадение '{'                              |
| 35  | `$ } <stmts> ; } <init_list>`                  | `1 , 2 , 3 } ; int c [ … $`      | `<init_list> → <assign_end> <init_rest>`    |
| 36  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `1 , 2 , 3 } ; int c [ … $`      | `<assign_end> → num`                        |
| 37  | `$ } <stmts> ; } <init_rest> num`              | `1 , 2 , 3 } ; int c [ … $`      | совпадение '1'                              |
| 38  | `$ } <stmts> ; } <init_rest>`                  | `, 2 , 3 } ; int c [ ] … $`      | `<init_rest> → , <assign_end> <init_rest>`  |
| 39  | `$ } <stmts> ; } <init_rest> <assign_end> ,`   | `, 2 , 3 } ; int c [ ] … $`      | совпадение ','                              |
| 40  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `2 , 3 } ; int c [ ] ; … $`      | `<assign_end> → num`                        |
| 41  | `$ } <stmts> ; } <init_rest> num`              | `2 , 3 } ; int c [ ] ; … $`      | совпадение '2'                              |
| 42  | `$ } <stmts> ; } <init_rest>`                  | `, 3 } ; int c [ ] ; int … $`    | `<init_rest> → , <assign_end> <init_rest>`  |
| 43  | `$ } <stmts> ; } <init_rest> <assign_end> ,`   | `, 3 } ; int c [ ] ; int … $`    | совпадение ','                              |
| 44  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `3 } ; int c [ ] ; int d … $`    | `<assign_end> → num`                        |
| 45  | `$ } <stmts> ; } <init_rest> num`              | `3 } ; int c [ ] ; int d … $`    | совпадение '3'                              |
| 46  | `$ } <stmts> ; } <init_rest>`                  | `} ; int c [ ] ; int d [ … $`    | `<init_rest> → ε`                           |
| 47  | `$ } <stmts> ; }`                              | `} ; int c [ ] ; int d [ … $`    | совпадение '}'                              |
| 48  | `$ } <stmts> ;`                                | `; int c [ ] ; int d [ 3 … $`    | совпадение ';'                              |
| 49  | `$ } <stmts>`                                  | `int c [ ] ; int d [ 3 ] … $`    | `<stmts> → <statement> <stmts>`             |
| 50  | `$ } <stmts> <statement>`                      | `int c [ ] ; int d [ 3 ] … $`    | `<statement> → <declaration> ;`             |
| 51  | `$ } <stmts> ; <declaration>`                  | `int c [ ] ; int d [ 3 ] … $`    | `<declaration> → <type> id <decl_tail>`     |
| 52  | `$ } <stmts> ; <decl_tail> id <type>`          | `int c [ ] ; int d [ 3 ] … $`    | `<type> → int`                              |
| 53  | `$ } <stmts> ; <decl_tail> id int`             | `int c [ ] ; int d [ 3 ] … $`    | совпадение 'int'                            |
| 54  | `$ } <stmts> ; <decl_tail> id`                 | `c [ ] ; int d [ 3 ] = … $`      | совпадение 'c'                              |
| 55  | `$ } <stmts> ; <decl_tail>`                    | `[ ] ; int d [ 3 ] = { … $`      | `<decl_tail> → [ <size> ] <array_init>`     |
| 56  | `$ } <stmts> ; <array_init> ] <size> [`        | `[ ] ; int d [ 3 ] = { … $`      | совпадение '['                              |
| 57  | `$ } <stmts> ; <array_init> ] <size>`          | `] ; int d [ 3 ] = { 1 … $`      | `<size> → ε`                                |
| 58  | `$ } <stmts> ; <array_init> ]`                 | `] ; int d [ 3 ] = { 1 … $`      | совпадение ']'                              |
| 59  | `$ } <stmts> ; <array_init>`                   | `; int d [ 3 ] = { 1 , … $`      | `<array_init> → ε`                          |
| 60  | `$ } <stmts> ;`                                | `; int d [ 3 ] = { 1 , … $`      | совпадение ';'                              |
| 61  | `$ } <stmts>`                                  | `int d [ 3 ] = { 1 , 2 … $`      | `<stmts> → <statement> <stmts>`             |
| 62  | `$ } <stmts> <statement>`                      | `int d [ 3 ] = { 1 , 2 … $`      | `<statement> → <declaration> ;`             |
| 63  | `$ } <stmts> ; <declaration>`                  | `int d [ 3 ] = { 1 , 2 … $`      | `<declaration> → <type> id <decl_tail>`     |
| 64  | `$ } <stmts> ; <decl_tail> id <type>`          | `int d [ 3 ] = { 1 , 2 … $`      | `<type> → int`                              |
| 65  | `$ } <stmts> ; <decl_tail> id int`             | `int d [ 3 ] = { 1 , 2 … $`      | совпадение 'int'                            |
| 66  | `$ } <stmts> ; <decl_tail> id`                 | `d [ 3 ] = { 1 , 2 , … $`        | совпадение 'd'                              |
| 67  | `$ } <stmts> ; <decl_tail>`                    | `[ 3 ] = { 1 , 2 , 3 … $`        | `<decl_tail> → [ <size> ] <array_init>`     |
| 68  | `$ } <stmts> ; <array_init> ] <size> [`        | `[ 3 ] = { 1 , 2 , 3 … $`        | совпадение '['                              |
| 69  | `$ } <stmts> ; <array_init> ] <size>`          | `3 ] = { 1 , 2 , 3 } … $`        | `<size> → num`                              |
| 70  | `$ } <stmts> ; <array_init> ] num`             | `3 ] = { 1 , 2 , 3 } … $`        | совпадение '3'                              |
| 71  | `$ } <stmts> ; <array_init> ]`                 | `] = { 1 , 2 , 3 } ; … $`        | совпадение ']'                              |
| 72  | `$ } <stmts> ; <array_init>`                   | `= { 1 , 2 , 3 } ; int … $`      | `<array_init> → = { <init_list> }`          |
| 73  | `$ } <stmts> ; } <init_list> { =`              | `= { 1 , 2 , 3 } ; int … $`      | совпадение '='                              |
| 74  | `$ } <stmts> ; } <init_list> {`                | `{ 1 , 2 , 3 } ; int x … $`      | совпадение '{'                              |
| 75  | `$ } <stmts> ; } <init_list>`                  | `1 , 2 , 3 } ; int x = … $`      | `<init_list> → <assign_end> <init_rest>`    |
| 76  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `1 , 2 , 3 } ; int x = … $`      | `<assign_end> → num`                        |
| 77  | `$ } <stmts> ; } <init_rest> num`              | `1 , 2 , 3 } ; int x = … $`      | совпадение '1'                              |
| 78  | `$ } <stmts> ; } <init_rest>`                  | `, 2 , 3 } ; int x = d … $`      | `<init_rest> → , <assign_end> <init_rest>`  |
| 79  | `$ } <stmts> ; } <init_rest> <assign_end> ,`   | `, 2 , 3 } ; int x = d … $`      | совпадение ','                              |
| 80  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `2 , 3 } ; int x = d [ … $`      | `<assign_end> → num`                        |
| 81  | `$ } <stmts> ; } <init_rest> num`              | `2 , 3 } ; int x = d [ … $`      | совпадение '2'                              |
| 82  | `$ } <stmts> ; } <init_rest>`                  | `, 3 } ; int x = d [ 3 … $`      | `<init_rest> → , <assign_end> <init_rest>`  |
| 83  | `$ } <stmts> ; } <init_rest> <assign_end> ,`   | `, 3 } ; int x = d [ 3 … $`      | совпадение ','                              |
| 84  | `$ } <stmts> ; } <init_rest> <assign_end>`     | `3 } ; int x = d [ 3 ] … $`      | `<assign_end> → num`                        |
| 85  | `$ } <stmts> ; } <init_rest> num`              | `3 } ; int x = d [ 3 ] … $`      | совпадение '3'                              |
| 86  | `$ } <stmts> ; } <init_rest>`                  | `} ; int x = d [ 3 ] ; … $`      | `<init_rest> → ε`                           |
| 87  | `$ } <stmts> ; }`                              | `} ; int x = d [ 3 ] ; … $`      | совпадение '}'                              |
| 88  | `$ } <stmts> ;`                                | `; int x = d [ 3 ] ; int … $`    | совпадение ';'                              |
| 89  | `$ } <stmts>`                                  | `int x = d [ 3 ] ; int y … $`    | `<stmts> → <statement> <stmts>`             |
| 90  | `$ } <stmts> <statement>`                      | `int x = d [ 3 ] ; int y … $`    | `<statement> → <declaration> ;`             |
| 91  | `$ } <stmts> ; <declaration>`                  | `int x = d [ 3 ] ; int y … $`    | `<declaration> → <type> id <decl_tail>`     |
| 92  | `$ } <stmts> ; <decl_tail> id <type>`          | `int x = d [ 3 ] ; int y … $`    | `<type> → int`                              |
| 93  | `$ } <stmts> ; <decl_tail> id int`             | `int x = d [ 3 ] ; int y … $`    | совпадение 'int'                            |
| 94  | `$ } <stmts> ; <decl_tail> id`                 | `x = d [ 3 ] ; int y = … $`      | совпадение 'x'                              |
| 95  | `$ } <stmts> ; <decl_tail>`                    | `= d [ 3 ] ; int y = 5 … $`      | `<decl_tail> → <assign>`                    |
| 96  | `$ } <stmts> ; <assign>`                       | `= d [ 3 ] ; int y = 5 … $`      | `<assign> → = <assign_end>`                 |
| 97  | `$ } <stmts> ; <assign_end> =`                 | `= d [ 3 ] ; int y = 5 … $`      | совпадение '='                              |
| 98  | `$ } <stmts> ; <assign_end>`                   | `d [ 3 ] ; int y = 5 ; … $`      | `<assign_end> → id <index>`                 |
| 99  | `$ } <stmts> ; <index> id`                     | `d [ 3 ] ; int y = 5 ; … $`      | совпадение 'd'                              |
| 100 | `$ } <stmts> ; <index>`                        | `[ 3 ] ; int y = 5 ; y … $`      | `<index> → [ <subscript> ]`                 |
| 101 | `$ } <stmts> ; ] <subscript> [`                | `[ 3 ] ; int y = 5 ; y … $`      | совпадение '['                              |
| 102 | `$ } <stmts> ; ] <subscript>`                  | `3 ] ; int y = 5 ; y [ … $`      | `<subscript> → num`                         |
| 103 | `$ } <stmts> ; ] num`                          | `3 ] ; int y = 5 ; y [ … $`      | совпадение '3'                              |
| 104 | `$ } <stmts> ; ]`                              | `] ; int y = 5 ; y [ 0 … $`      | совпадение ']'                              |
| 105 | `$ } <stmts> ;`                                | `; int y = 5 ; y [ 0 ] … $`      | совпадение ';'                              |
| 106 | `$ } <stmts>`                                  | `int y = 5 ; y [ 0 ] = … $`      | `<stmts> → <statement> <stmts>`             |
| 107 | `$ } <stmts> <statement>`                      | `int y = 5 ; y [ 0 ] = … $`      | `<statement> → <declaration> ;`             |
| 108 | `$ } <stmts> ; <declaration>`                  | `int y = 5 ; y [ 0 ] = … $`      | `<declaration> → <type> id <decl_tail>`     |
| 109 | `$ } <stmts> ; <decl_tail> id <type>`          | `int y = 5 ; y [ 0 ] = … $`      | `<type> → int`                              |
| 110 | `$ } <stmts> ; <decl_tail> id int`             | `int y = 5 ; y [ 0 ] = … $`      | совпадение 'int'                            |
| 111 | `$ } <stmts> ; <decl_tail> id`                 | `y = 5 ; y [ 0 ] = 1 … $`        | совпадение 'y'                              |
| 112 | `$ } <stmts> ; <decl_tail>`                    | `= 5 ; y [ 0 ] = 1 ; … $`        | `<decl_tail> → <assign>`                    |
| 113 | `$ } <stmts> ; <assign>`                       | `= 5 ; y [ 0 ] = 1 ; … $`        | `<assign> → = <assign_end>`                 |
| 114 | `$ } <stmts> ; <assign_end> =`                 | `= 5 ; y [ 0 ] = 1 ; … $`        | совпадение '='                              |
| 115 | `$ } <stmts> ; <assign_end>`                   | `5 ; y [ 0 ] = 1 ; int … $`      | `<assign_end> → num`                        |
| 116 | `$ } <stmts> ; num`                            | `5 ; y [ 0 ] = 1 ; int … $`      | совпадение '5'                              |
| 117 | `$ } <stmts> ;`                                | `; y [ 0 ] = 1 ; int z … $`      | совпадение ';'                              |
| 118 | `$ } <stmts>`                                  | `y [ 0 ] = 1 ; int z = … $`      | `<stmts> → <statement> <stmts>`             |
| 119 | `$ } <stmts> <statement>`                      | `y [ 0 ] = 1 ; int z = … $`      | `<statement> → id <index> = <assign_end> ;` |
| 120 | `$ } <stmts> ; <assign_end> = <index> id`      | `y [ 0 ] = 1 ; int z = … $`      | совпадение 'y'                              |
| 121 | `$ } <stmts> ; <assign_end> = <index>`         | `[ 0 ] = 1 ; int z = d … $`      | `<index> → [ <subscript> ]`                 |
| 122 | `$ } <stmts> ; <assign_end> = ] <subscript> [` | `[ 0 ] = 1 ; int z = d … $`      | совпадение '['                              |
| 123 | `$ } <stmts> ; <assign_end> = ] <subscript>`   | `0 ] = 1 ; int z = d ; … $`      | `<subscript> → num`                         |
| 124 | `$ } <stmts> ; <assign_end> = ] num`           | `0 ] = 1 ; int z = d ; … $`      | совпадение '0'                              |
| 125 | `$ } <stmts> ; <assign_end> = ]`               | `] = 1 ; int z = d ; return … $` | совпадение ']'                              |
| 126 | `$ } <stmts> ; <assign_end> =`                 | `= 1 ; int z = d ; return 0 … $` | совпадение '='                              |
| 127 | `$ } <stmts> ; <assign_end>`                   | `1 ; int z = d ; return 0 ; … $` | `<assign_end> → num`                        |
| 128 | `$ } <stmts> ; num`                            | `1 ; int z = d ; return 0 ; … $` | совпадение '1'                              |
| 129 | `$ } <stmts> ;`                                | `; int z = d ; return 0 ; } $`   | совпадение ';'                              |
| 130 | `$ } <stmts>`                                  | `int z = d ; return 0 ; } $`     | `<stmts> → <statement> <stmts>`             |
| 131 | `$ } <stmts> <statement>`                      | `int z = d ; return 0 ; } $`     | `<statement> → <declaration> ;`             |
| 132 | `$ } <stmts> ; <declaration>`                  | `int z = d ; return 0 ; } $`     | `<declaration> → <type> id <decl_tail>`     |
| 133 | `$ } <stmts> ; <decl_tail> id <type>`          | `int z = d ; return 0 ; } $`     | `<type> → int`                              |
| 134 | `$ } <stmts> ; <decl_tail> id int`             | `int z = d ; return 0 ; } $`     | совпадение 'int'                            |
| 135 | `$ } <stmts> ; <decl_tail> id`                 | `z = d ; return 0 ; } $`         | совпадение 'z'                              |
| 136 | `$ } <stmts> ; <decl_tail>`                    | `= d ; return 0 ; } $`           | `<decl_tail> → <assign>`                    |
| 137 | `$ } <stmts> ; <assign>`                       | `= d ; return 0 ; } $`           | `<assign> → = <assign_end>`                 |
| 138 | `$ } <stmts> ; <assign_end> =`                 | `= d ; return 0 ; } $`           | совпадение '='                              |
| 139 | `$ } <stmts> ; <assign_end>`                   | `d ; return 0 ; } $`             | `<assign_end> → id <index>`                 |
| 140 | `$ } <stmts> ; <index> id`                     | `d ; return 0 ; } $`             | совпадение 'd'                              |
| 141 | `$ } <stmts> ; <index>`                        | `; return 0 ; } $`               | `<index> → ε`                               |
| 142 | `$ } <stmts> ;`                                | `; return 0 ; } $`               | совпадение ';'                              |
| 143 | `$ } <stmts>`                                  | `return 0 ; } $`                 | `<stmts> → <statement> <stmts>`             |
| 144 | `$ } <stmts> <statement>`                      | `return 0 ; } $`                 | `<statement> → <return>`                    |
| 145 | `$ } <stmts> <return>`                         | `return 0 ; } $`                 | `<return> → return num ;`                   |
| 146 | `$ } <stmts> ; num return`                     | `return 0 ; } $`                 | совпадение 'return'                         |
| 147 | `$ } <stmts> ; num`                            | `0 ; } $`                        | совпадение '0'                              |
| 148 | `$ } <stmts> ;`                                | `; } $`                          | совпадение ';'                              |
| 149 | `$ } <stmts>`                                  | `} $`                            | `<stmts> → ε`                               |
| 150 | `$ }`                                          | `} $`                            | совпадение '}'                              |
| 151 | `$`                                            | `$`                              | Разбор завершён, ошибок нет                 |
