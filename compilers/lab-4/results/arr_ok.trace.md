# Ход разбора: arr_ok.cl

Грамматика: с массивами (--arrays), восстановление: режим паники.

## Исходный текст

```c
// Массивы без ошибок: объявление, инициализация, обращение к ячейкам, присваивание.
// флаги: --arrays
// ожидается: panic=0 phrase=0
int main() {
    int a[3];
    int b[5] = {1, 2, 3};
    int c[] = {4, 5};
    int n = 2;
    a[0] = 7;
    a[n] = b[1];
    int x = c[1];
    for (int i = 0; i < n;) {
        if (a[i] == b[i]) return 0;
        c[0] = i;
    }
    if (1 < a[2]) return 1;
    return 2;
}
```

## Ошибки (0)

Ошибок нет.

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                                                     | Вход                                | Примечание                                            |
|-----|--------------------------------------------------------------------------|-------------------------------------|-------------------------------------------------------|
| 1   | `$ <program>`                                                            | `int main ( ) { int a [ 3 ] … $`    | `<program> → <type> main ( ) { <stmts> }`             |
| 2   | `$ } <stmts> { ) ( main <type>`                                          | `int main ( ) { int a [ 3 ] … $`    | `<type> → int`                                        |
| 3   | `$ } <stmts> { ) ( main int`                                             | `int main ( ) { int a [ 3 ] … $`    | совпадение 'int'                                      |
| 4   | `$ } <stmts> { ) ( main`                                                 | `main ( ) { int a [ 3 ] ; … $`      | совпадение 'main'                                     |
| 5   | `$ } <stmts> { ) (`                                                      | `( ) { int a [ 3 ] ; int … $`       | совпадение '('                                        |
| 6   | `$ } <stmts> { )`                                                        | `) { int a [ 3 ] ; int b … $`       | совпадение ')'                                        |
| 7   | `$ } <stmts> {`                                                          | `{ int a [ 3 ] ; int b [ … $`       | совпадение '{'                                        |
| 8   | `$ } <stmts>`                                                            | `int a [ 3 ] ; int b [ 5 … $`       | `<stmts> → <statement> <stmts>`                       |
| 9   | `$ } <stmts> <statement>`                                                | `int a [ 3 ] ; int b [ 5 … $`       | `<statement> → <declaration> ;`                       |
| 10  | `$ } <stmts> ; <declaration>`                                            | `int a [ 3 ] ; int b [ 5 … $`       | `<declaration> → <type> id <decl_tail>`               |
| 11  | `$ } <stmts> ; <decl_tail> id <type>`                                    | `int a [ 3 ] ; int b [ 5 … $`       | `<type> → int`                                        |
| 12  | `$ } <stmts> ; <decl_tail> id int`                                       | `int a [ 3 ] ; int b [ 5 … $`       | совпадение 'int'                                      |
| 13  | `$ } <stmts> ; <decl_tail> id`                                           | `a [ 3 ] ; int b [ 5 ] … $`         | совпадение 'a'                                        |
| 14  | `$ } <stmts> ; <decl_tail>`                                              | `[ 3 ] ; int b [ 5 ] = … $`         | `<decl_tail> → [ <size> ] <array_init>`               |
| 15  | `$ } <stmts> ; <array_init> ] <size> [`                                  | `[ 3 ] ; int b [ 5 ] = … $`         | совпадение '['                                        |
| 16  | `$ } <stmts> ; <array_init> ] <size>`                                    | `3 ] ; int b [ 5 ] = { … $`         | `<size> → num`                                        |
| 17  | `$ } <stmts> ; <array_init> ] num`                                       | `3 ] ; int b [ 5 ] = { … $`         | совпадение '3'                                        |
| 18  | `$ } <stmts> ; <array_init> ]`                                           | `] ; int b [ 5 ] = { 1 … $`         | совпадение ']'                                        |
| 19  | `$ } <stmts> ; <array_init>`                                             | `; int b [ 5 ] = { 1 , … $`         | `<array_init> → ε`                                    |
| 20  | `$ } <stmts> ;`                                                          | `; int b [ 5 ] = { 1 , … $`         | совпадение ';'                                        |
| 21  | `$ } <stmts>`                                                            | `int b [ 5 ] = { 1 , 2 … $`         | `<stmts> → <statement> <stmts>`                       |
| 22  | `$ } <stmts> <statement>`                                                | `int b [ 5 ] = { 1 , 2 … $`         | `<statement> → <declaration> ;`                       |
| 23  | `$ } <stmts> ; <declaration>`                                            | `int b [ 5 ] = { 1 , 2 … $`         | `<declaration> → <type> id <decl_tail>`               |
| 24  | `$ } <stmts> ; <decl_tail> id <type>`                                    | `int b [ 5 ] = { 1 , 2 … $`         | `<type> → int`                                        |
| 25  | `$ } <stmts> ; <decl_tail> id int`                                       | `int b [ 5 ] = { 1 , 2 … $`         | совпадение 'int'                                      |
| 26  | `$ } <stmts> ; <decl_tail> id`                                           | `b [ 5 ] = { 1 , 2 , … $`           | совпадение 'b'                                        |
| 27  | `$ } <stmts> ; <decl_tail>`                                              | `[ 5 ] = { 1 , 2 , 3 … $`           | `<decl_tail> → [ <size> ] <array_init>`               |
| 28  | `$ } <stmts> ; <array_init> ] <size> [`                                  | `[ 5 ] = { 1 , 2 , 3 … $`           | совпадение '['                                        |
| 29  | `$ } <stmts> ; <array_init> ] <size>`                                    | `5 ] = { 1 , 2 , 3 } … $`           | `<size> → num`                                        |
| 30  | `$ } <stmts> ; <array_init> ] num`                                       | `5 ] = { 1 , 2 , 3 } … $`           | совпадение '5'                                        |
| 31  | `$ } <stmts> ; <array_init> ]`                                           | `] = { 1 , 2 , 3 } ; … $`           | совпадение ']'                                        |
| 32  | `$ } <stmts> ; <array_init>`                                             | `= { 1 , 2 , 3 } ; int … $`         | `<array_init> → = { <init_list> }`                    |
| 33  | `$ } <stmts> ; } <init_list> { =`                                        | `= { 1 , 2 , 3 } ; int … $`         | совпадение '='                                        |
| 34  | `$ } <stmts> ; } <init_list> {`                                          | `{ 1 , 2 , 3 } ; int c … $`         | совпадение '{'                                        |
| 35  | `$ } <stmts> ; } <init_list>`                                            | `1 , 2 , 3 } ; int c [ … $`         | `<init_list> → <assign_end> <init_rest>`              |
| 36  | `$ } <stmts> ; } <init_rest> <assign_end>`                               | `1 , 2 , 3 } ; int c [ … $`         | `<assign_end> → num`                                  |
| 37  | `$ } <stmts> ; } <init_rest> num`                                        | `1 , 2 , 3 } ; int c [ … $`         | совпадение '1'                                        |
| 38  | `$ } <stmts> ; } <init_rest>`                                            | `, 2 , 3 } ; int c [ ] … $`         | `<init_rest> → , <assign_end> <init_rest>`            |
| 39  | `$ } <stmts> ; } <init_rest> <assign_end> ,`                             | `, 2 , 3 } ; int c [ ] … $`         | совпадение ','                                        |
| 40  | `$ } <stmts> ; } <init_rest> <assign_end>`                               | `2 , 3 } ; int c [ ] = … $`         | `<assign_end> → num`                                  |
| 41  | `$ } <stmts> ; } <init_rest> num`                                        | `2 , 3 } ; int c [ ] = … $`         | совпадение '2'                                        |
| 42  | `$ } <stmts> ; } <init_rest>`                                            | `, 3 } ; int c [ ] = { … $`         | `<init_rest> → , <assign_end> <init_rest>`            |
| 43  | `$ } <stmts> ; } <init_rest> <assign_end> ,`                             | `, 3 } ; int c [ ] = { … $`         | совпадение ','                                        |
| 44  | `$ } <stmts> ; } <init_rest> <assign_end>`                               | `3 } ; int c [ ] = { 4 … $`         | `<assign_end> → num`                                  |
| 45  | `$ } <stmts> ; } <init_rest> num`                                        | `3 } ; int c [ ] = { 4 … $`         | совпадение '3'                                        |
| 46  | `$ } <stmts> ; } <init_rest>`                                            | `} ; int c [ ] = { 4 , … $`         | `<init_rest> → ε`                                     |
| 47  | `$ } <stmts> ; }`                                                        | `} ; int c [ ] = { 4 , … $`         | совпадение '}'                                        |
| 48  | `$ } <stmts> ;`                                                          | `; int c [ ] = { 4 , 5 … $`         | совпадение ';'                                        |
| 49  | `$ } <stmts>`                                                            | `int c [ ] = { 4 , 5 } … $`         | `<stmts> → <statement> <stmts>`                       |
| 50  | `$ } <stmts> <statement>`                                                | `int c [ ] = { 4 , 5 } … $`         | `<statement> → <declaration> ;`                       |
| 51  | `$ } <stmts> ; <declaration>`                                            | `int c [ ] = { 4 , 5 } … $`         | `<declaration> → <type> id <decl_tail>`               |
| 52  | `$ } <stmts> ; <decl_tail> id <type>`                                    | `int c [ ] = { 4 , 5 } … $`         | `<type> → int`                                        |
| 53  | `$ } <stmts> ; <decl_tail> id int`                                       | `int c [ ] = { 4 , 5 } … $`         | совпадение 'int'                                      |
| 54  | `$ } <stmts> ; <decl_tail> id`                                           | `c [ ] = { 4 , 5 } ; … $`           | совпадение 'c'                                        |
| 55  | `$ } <stmts> ; <decl_tail>`                                              | `[ ] = { 4 , 5 } ; int … $`         | `<decl_tail> → [ <size> ] <array_init>`               |
| 56  | `$ } <stmts> ; <array_init> ] <size> [`                                  | `[ ] = { 4 , 5 } ; int … $`         | совпадение '['                                        |
| 57  | `$ } <stmts> ; <array_init> ] <size>`                                    | `] = { 4 , 5 } ; int n … $`         | `<size> → ε`                                          |
| 58  | `$ } <stmts> ; <array_init> ]`                                           | `] = { 4 , 5 } ; int n … $`         | совпадение ']'                                        |
| 59  | `$ } <stmts> ; <array_init>`                                             | `= { 4 , 5 } ; int n = … $`         | `<array_init> → = { <init_list> }`                    |
| 60  | `$ } <stmts> ; } <init_list> { =`                                        | `= { 4 , 5 } ; int n = … $`         | совпадение '='                                        |
| 61  | `$ } <stmts> ; } <init_list> {`                                          | `{ 4 , 5 } ; int n = 2 … $`         | совпадение '{'                                        |
| 62  | `$ } <stmts> ; } <init_list>`                                            | `4 , 5 } ; int n = 2 ; … $`         | `<init_list> → <assign_end> <init_rest>`              |
| 63  | `$ } <stmts> ; } <init_rest> <assign_end>`                               | `4 , 5 } ; int n = 2 ; … $`         | `<assign_end> → num`                                  |
| 64  | `$ } <stmts> ; } <init_rest> num`                                        | `4 , 5 } ; int n = 2 ; … $`         | совпадение '4'                                        |
| 65  | `$ } <stmts> ; } <init_rest>`                                            | `, 5 } ; int n = 2 ; a … $`         | `<init_rest> → , <assign_end> <init_rest>`            |
| 66  | `$ } <stmts> ; } <init_rest> <assign_end> ,`                             | `, 5 } ; int n = 2 ; a … $`         | совпадение ','                                        |
| 67  | `$ } <stmts> ; } <init_rest> <assign_end>`                               | `5 } ; int n = 2 ; a [ … $`         | `<assign_end> → num`                                  |
| 68  | `$ } <stmts> ; } <init_rest> num`                                        | `5 } ; int n = 2 ; a [ … $`         | совпадение '5'                                        |
| 69  | `$ } <stmts> ; } <init_rest>`                                            | `} ; int n = 2 ; a [ 0 … $`         | `<init_rest> → ε`                                     |
| 70  | `$ } <stmts> ; }`                                                        | `} ; int n = 2 ; a [ 0 … $`         | совпадение '}'                                        |
| 71  | `$ } <stmts> ;`                                                          | `; int n = 2 ; a [ 0 ] … $`         | совпадение ';'                                        |
| 72  | `$ } <stmts>`                                                            | `int n = 2 ; a [ 0 ] = … $`         | `<stmts> → <statement> <stmts>`                       |
| 73  | `$ } <stmts> <statement>`                                                | `int n = 2 ; a [ 0 ] = … $`         | `<statement> → <declaration> ;`                       |
| 74  | `$ } <stmts> ; <declaration>`                                            | `int n = 2 ; a [ 0 ] = … $`         | `<declaration> → <type> id <decl_tail>`               |
| 75  | `$ } <stmts> ; <decl_tail> id <type>`                                    | `int n = 2 ; a [ 0 ] = … $`         | `<type> → int`                                        |
| 76  | `$ } <stmts> ; <decl_tail> id int`                                       | `int n = 2 ; a [ 0 ] = … $`         | совпадение 'int'                                      |
| 77  | `$ } <stmts> ; <decl_tail> id`                                           | `n = 2 ; a [ 0 ] = 7 … $`           | совпадение 'n'                                        |
| 78  | `$ } <stmts> ; <decl_tail>`                                              | `= 2 ; a [ 0 ] = 7 ; … $`           | `<decl_tail> → <assign>`                              |
| 79  | `$ } <stmts> ; <assign>`                                                 | `= 2 ; a [ 0 ] = 7 ; … $`           | `<assign> → = <assign_end>`                           |
| 80  | `$ } <stmts> ; <assign_end> =`                                           | `= 2 ; a [ 0 ] = 7 ; … $`           | совпадение '='                                        |
| 81  | `$ } <stmts> ; <assign_end>`                                             | `2 ; a [ 0 ] = 7 ; a … $`           | `<assign_end> → num`                                  |
| 82  | `$ } <stmts> ; num`                                                      | `2 ; a [ 0 ] = 7 ; a … $`           | совпадение '2'                                        |
| 83  | `$ } <stmts> ;`                                                          | `; a [ 0 ] = 7 ; a [ … $`           | совпадение ';'                                        |
| 84  | `$ } <stmts>`                                                            | `a [ 0 ] = 7 ; a [ n … $`           | `<stmts> → <statement> <stmts>`                       |
| 85  | `$ } <stmts> <statement>`                                                | `a [ 0 ] = 7 ; a [ n … $`           | `<statement> → id <index> = <assign_end> ;`           |
| 86  | `$ } <stmts> ; <assign_end> = <index> id`                                | `a [ 0 ] = 7 ; a [ n … $`           | совпадение 'a'                                        |
| 87  | `$ } <stmts> ; <assign_end> = <index>`                                   | `[ 0 ] = 7 ; a [ n ] … $`           | `<index> → [ <subscript> ]`                           |
| 88  | `$ } <stmts> ; <assign_end> = ] <subscript> [`                           | `[ 0 ] = 7 ; a [ n ] … $`           | совпадение '['                                        |
| 89  | `$ } <stmts> ; <assign_end> = ] <subscript>`                             | `0 ] = 7 ; a [ n ] = … $`           | `<subscript> → num`                                   |
| 90  | `$ } <stmts> ; <assign_end> = ] num`                                     | `0 ] = 7 ; a [ n ] = … $`           | совпадение '0'                                        |
| 91  | `$ } <stmts> ; <assign_end> = ]`                                         | `] = 7 ; a [ n ] = b … $`           | совпадение ']'                                        |
| 92  | `$ } <stmts> ; <assign_end> =`                                           | `= 7 ; a [ n ] = b [ … $`           | совпадение '='                                        |
| 93  | `$ } <stmts> ; <assign_end>`                                             | `7 ; a [ n ] = b [ 1 … $`           | `<assign_end> → num`                                  |
| 94  | `$ } <stmts> ; num`                                                      | `7 ; a [ n ] = b [ 1 … $`           | совпадение '7'                                        |
| 95  | `$ } <stmts> ;`                                                          | `; a [ n ] = b [ 1 ] … $`           | совпадение ';'                                        |
| 96  | `$ } <stmts>`                                                            | `a [ n ] = b [ 1 ] ; … $`           | `<stmts> → <statement> <stmts>`                       |
| 97  | `$ } <stmts> <statement>`                                                | `a [ n ] = b [ 1 ] ; … $`           | `<statement> → id <index> = <assign_end> ;`           |
| 98  | `$ } <stmts> ; <assign_end> = <index> id`                                | `a [ n ] = b [ 1 ] ; … $`           | совпадение 'a'                                        |
| 99  | `$ } <stmts> ; <assign_end> = <index>`                                   | `[ n ] = b [ 1 ] ; int … $`         | `<index> → [ <subscript> ]`                           |
| 100 | `$ } <stmts> ; <assign_end> = ] <subscript> [`                           | `[ n ] = b [ 1 ] ; int … $`         | совпадение '['                                        |
| 101 | `$ } <stmts> ; <assign_end> = ] <subscript>`                             | `n ] = b [ 1 ] ; int x … $`         | `<subscript> → id`                                    |
| 102 | `$ } <stmts> ; <assign_end> = ] id`                                      | `n ] = b [ 1 ] ; int x … $`         | совпадение 'n'                                        |
| 103 | `$ } <stmts> ; <assign_end> = ]`                                         | `] = b [ 1 ] ; int x = … $`         | совпадение ']'                                        |
| 104 | `$ } <stmts> ; <assign_end> =`                                           | `= b [ 1 ] ; int x = c … $`         | совпадение '='                                        |
| 105 | `$ } <stmts> ; <assign_end>`                                             | `b [ 1 ] ; int x = c [ … $`         | `<assign_end> → id <index>`                           |
| 106 | `$ } <stmts> ; <index> id`                                               | `b [ 1 ] ; int x = c [ … $`         | совпадение 'b'                                        |
| 107 | `$ } <stmts> ; <index>`                                                  | `[ 1 ] ; int x = c [ 1 … $`         | `<index> → [ <subscript> ]`                           |
| 108 | `$ } <stmts> ; ] <subscript> [`                                          | `[ 1 ] ; int x = c [ 1 … $`         | совпадение '['                                        |
| 109 | `$ } <stmts> ; ] <subscript>`                                            | `1 ] ; int x = c [ 1 ] … $`         | `<subscript> → num`                                   |
| 110 | `$ } <stmts> ; ] num`                                                    | `1 ] ; int x = c [ 1 ] … $`         | совпадение '1'                                        |
| 111 | `$ } <stmts> ; ]`                                                        | `] ; int x = c [ 1 ] ; … $`         | совпадение ']'                                        |
| 112 | `$ } <stmts> ;`                                                          | `; int x = c [ 1 ] ; for … $`       | совпадение ';'                                        |
| 113 | `$ } <stmts>`                                                            | `int x = c [ 1 ] ; for ( … $`       | `<stmts> → <statement> <stmts>`                       |
| 114 | `$ } <stmts> <statement>`                                                | `int x = c [ 1 ] ; for ( … $`       | `<statement> → <declaration> ;`                       |
| 115 | `$ } <stmts> ; <declaration>`                                            | `int x = c [ 1 ] ; for ( … $`       | `<declaration> → <type> id <decl_tail>`               |
| 116 | `$ } <stmts> ; <decl_tail> id <type>`                                    | `int x = c [ 1 ] ; for ( … $`       | `<type> → int`                                        |
| 117 | `$ } <stmts> ; <decl_tail> id int`                                       | `int x = c [ 1 ] ; for ( … $`       | совпадение 'int'                                      |
| 118 | `$ } <stmts> ; <decl_tail> id`                                           | `x = c [ 1 ] ; for ( int … $`       | совпадение 'x'                                        |
| 119 | `$ } <stmts> ; <decl_tail>`                                              | `= c [ 1 ] ; for ( int i … $`       | `<decl_tail> → <assign>`                              |
| 120 | `$ } <stmts> ; <assign>`                                                 | `= c [ 1 ] ; for ( int i … $`       | `<assign> → = <assign_end>`                           |
| 121 | `$ } <stmts> ; <assign_end> =`                                           | `= c [ 1 ] ; for ( int i … $`       | совпадение '='                                        |
| 122 | `$ } <stmts> ; <assign_end>`                                             | `c [ 1 ] ; for ( int i = … $`       | `<assign_end> → id <index>`                           |
| 123 | `$ } <stmts> ; <index> id`                                               | `c [ 1 ] ; for ( int i = … $`       | совпадение 'c'                                        |
| 124 | `$ } <stmts> ; <index>`                                                  | `[ 1 ] ; for ( int i = 0 … $`       | `<index> → [ <subscript> ]`                           |
| 125 | `$ } <stmts> ; ] <subscript> [`                                          | `[ 1 ] ; for ( int i = 0 … $`       | совпадение '['                                        |
| 126 | `$ } <stmts> ; ] <subscript>`                                            | `1 ] ; for ( int i = 0 ; … $`       | `<subscript> → num`                                   |
| 127 | `$ } <stmts> ; ] num`                                                    | `1 ] ; for ( int i = 0 ; … $`       | совпадение '1'                                        |
| 128 | `$ } <stmts> ; ]`                                                        | `] ; for ( int i = 0 ; i … $`       | совпадение ']'                                        |
| 129 | `$ } <stmts> ;`                                                          | `; for ( int i = 0 ; i < … $`       | совпадение ';'                                        |
| 130 | `$ } <stmts>`                                                            | `for ( int i = 0 ; i < n … $`       | `<stmts> → <statement> <stmts>`                       |
| 131 | `$ } <stmts> <statement>`                                                | `for ( int i = 0 ; i < n … $`       | `<statement> → <for> <statement>`                     |
| 132 | `$ } <stmts> <statement> <for>`                                          | `for ( int i = 0 ; i < n … $`       | `<for> → for ( <declaration> ; <bool_expression> ; )` |
| 133 | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> ( for`    | `for ( int i = 0 ; i < n … $`       | совпадение 'for'                                      |
| 134 | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration> (`        | `( int i = 0 ; i < n ; … $`         | совпадение '('                                        |
| 135 | `$ } <stmts> <statement> ) ; <bool_expression> ; <declaration>`          | `int i = 0 ; i < n ; ) … $`         | `<declaration> → <type> id <decl_tail>`               |
| 136 | `$ } <stmts> <statement> ) ; <bool_expression> ; <decl_tail> id <type>`  | `int i = 0 ; i < n ; ) … $`         | `<type> → int`                                        |
| 137 | `$ } <stmts> <statement> ) ; <bool_expression> ; <decl_tail> id int`     | `int i = 0 ; i < n ; ) … $`         | совпадение 'int'                                      |
| 138 | `$ } <stmts> <statement> ) ; <bool_expression> ; <decl_tail> id`         | `i = 0 ; i < n ; ) { … $`           | совпадение 'i'                                        |
| 139 | `$ } <stmts> <statement> ) ; <bool_expression> ; <decl_tail>`            | `= 0 ; i < n ; ) { if … $`          | `<decl_tail> → <assign>`                              |
| 140 | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign>`               | `= 0 ; i < n ; ) { if … $`          | `<assign> → = <assign_end>`                           |
| 141 | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end> =`         | `= 0 ; i < n ; ) { if … $`          | совпадение '='                                        |
| 142 | `$ } <stmts> <statement> ) ; <bool_expression> ; <assign_end>`           | `0 ; i < n ; ) { if ( … $`          | `<assign_end> → num`                                  |
| 143 | `$ } <stmts> <statement> ) ; <bool_expression> ; num`                    | `0 ; i < n ; ) { if ( … $`          | совпадение '0'                                        |
| 144 | `$ } <stmts> <statement> ) ; <bool_expression> ;`                        | `; i < n ; ) { if ( a … $`          | совпадение ';'                                        |
| 145 | `$ } <stmts> <statement> ) ; <bool_expression>`                          | `i < n ; ) { if ( a [ … $`          | `<bool_expression> → id <index> <relop> id <index>`   |
| 146 | `$ } <stmts> <statement> ) ; <index> id <relop> <index> id`              | `i < n ; ) { if ( a [ … $`          | совпадение 'i'                                        |
| 147 | `$ } <stmts> <statement> ) ; <index> id <relop> <index>`                 | `< n ; ) { if ( a [ i … $`          | `<index> → ε`                                         |
| 148 | `$ } <stmts> <statement> ) ; <index> id <relop>`                         | `< n ; ) { if ( a [ i … $`          | `<relop> → <`                                         |
| 149 | `$ } <stmts> <statement> ) ; <index> id <`                               | `< n ; ) { if ( a [ i … $`          | совпадение '<'                                        |
| 150 | `$ } <stmts> <statement> ) ; <index> id`                                 | `n ; ) { if ( a [ i ] … $`          | совпадение 'n'                                        |
| 151 | `$ } <stmts> <statement> ) ; <index>`                                    | `; ) { if ( a [ i ] == … $`         | `<index> → ε`                                         |
| 152 | `$ } <stmts> <statement> ) ;`                                            | `; ) { if ( a [ i ] == … $`         | совпадение ';'                                        |
| 153 | `$ } <stmts> <statement> )`                                              | `) { if ( a [ i ] == b … $`         | совпадение ')'                                        |
| 154 | `$ } <stmts> <statement>`                                                | `{ if ( a [ i ] == b [ … $`         | `<statement> → { <stmts> }`                           |
| 155 | `$ } <stmts> } <stmts> {`                                                | `{ if ( a [ i ] == b [ … $`         | совпадение '{'                                        |
| 156 | `$ } <stmts> } <stmts>`                                                  | `if ( a [ i ] == b [ i … $`         | `<stmts> → <statement> <stmts>`                       |
| 157 | `$ } <stmts> } <stmts> <statement>`                                      | `if ( a [ i ] == b [ i … $`         | `<statement> → <if> <statement>`                      |
| 158 | `$ } <stmts> } <stmts> <statement> <if>`                                 | `if ( a [ i ] == b [ i … $`         | `<if> → if ( <bool_expression> )`                     |
| 159 | `$ } <stmts> } <stmts> <statement> ) <bool_expression> ( if`             | `if ( a [ i ] == b [ i … $`         | совпадение 'if'                                       |
| 160 | `$ } <stmts> } <stmts> <statement> ) <bool_expression> (`                | `( a [ i ] == b [ i ] … $`          | совпадение '('                                        |
| 161 | `$ } <stmts> } <stmts> <statement> ) <bool_expression>`                  | `a [ i ] == b [ i ] ) … $`          | `<bool_expression> → id <index> <relop> id <index>`   |
| 162 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> <index> id`      | `a [ i ] == b [ i ] ) … $`          | совпадение 'a'                                        |
| 163 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> <index>`         | `[ i ] == b [ i ] ) return … $`     | `<index> → [ <subscript> ]`                           |
| 164 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> ] <subscript> [` | `[ i ] == b [ i ] ) return … $`     | совпадение '['                                        |
| 165 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> ] <subscript>`   | `i ] == b [ i ] ) return 0 … $`     | `<subscript> → id`                                    |
| 166 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> ] id`            | `i ] == b [ i ] ) return 0 … $`     | совпадение 'i'                                        |
| 167 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop> ]`               | `] == b [ i ] ) return 0 ; … $`     | совпадение ']'                                        |
| 168 | `$ } <stmts> } <stmts> <statement> ) <index> id <relop>`                 | `== b [ i ] ) return 0 ; c … $`     | `<relop> → ==`                                        |
| 169 | `$ } <stmts> } <stmts> <statement> ) <index> id ==`                      | `== b [ i ] ) return 0 ; c … $`     | совпадение '=='                                       |
| 170 | `$ } <stmts> } <stmts> <statement> ) <index> id`                         | `b [ i ] ) return 0 ; c [ … $`      | совпадение 'b'                                        |
| 171 | `$ } <stmts> } <stmts> <statement> ) <index>`                            | `[ i ] ) return 0 ; c [ 0 … $`      | `<index> → [ <subscript> ]`                           |
| 172 | `$ } <stmts> } <stmts> <statement> ) ] <subscript> [`                    | `[ i ] ) return 0 ; c [ 0 … $`      | совпадение '['                                        |
| 173 | `$ } <stmts> } <stmts> <statement> ) ] <subscript>`                      | `i ] ) return 0 ; c [ 0 ] … $`      | `<subscript> → id`                                    |
| 174 | `$ } <stmts> } <stmts> <statement> ) ] id`                               | `i ] ) return 0 ; c [ 0 ] … $`      | совпадение 'i'                                        |
| 175 | `$ } <stmts> } <stmts> <statement> ) ]`                                  | `] ) return 0 ; c [ 0 ] = … $`      | совпадение ']'                                        |
| 176 | `$ } <stmts> } <stmts> <statement> )`                                    | `) return 0 ; c [ 0 ] = i … $`      | совпадение ')'                                        |
| 177 | `$ } <stmts> } <stmts> <statement>`                                      | `return 0 ; c [ 0 ] = i ; … $`      | `<statement> → <return>`                              |
| 178 | `$ } <stmts> } <stmts> <return>`                                         | `return 0 ; c [ 0 ] = i ; … $`      | `<return> → return num ;`                             |
| 179 | `$ } <stmts> } <stmts> ; num return`                                     | `return 0 ; c [ 0 ] = i ; … $`      | совпадение 'return'                                   |
| 180 | `$ } <stmts> } <stmts> ; num`                                            | `0 ; c [ 0 ] = i ; } … $`           | совпадение '0'                                        |
| 181 | `$ } <stmts> } <stmts> ;`                                                | `; c [ 0 ] = i ; } if … $`          | совпадение ';'                                        |
| 182 | `$ } <stmts> } <stmts>`                                                  | `c [ 0 ] = i ; } if ( … $`          | `<stmts> → <statement> <stmts>`                       |
| 183 | `$ } <stmts> } <stmts> <statement>`                                      | `c [ 0 ] = i ; } if ( … $`          | `<statement> → id <index> = <assign_end> ;`           |
| 184 | `$ } <stmts> } <stmts> ; <assign_end> = <index> id`                      | `c [ 0 ] = i ; } if ( … $`          | совпадение 'c'                                        |
| 185 | `$ } <stmts> } <stmts> ; <assign_end> = <index>`                         | `[ 0 ] = i ; } if ( 1 … $`          | `<index> → [ <subscript> ]`                           |
| 186 | `$ } <stmts> } <stmts> ; <assign_end> = ] <subscript> [`                 | `[ 0 ] = i ; } if ( 1 … $`          | совпадение '['                                        |
| 187 | `$ } <stmts> } <stmts> ; <assign_end> = ] <subscript>`                   | `0 ] = i ; } if ( 1 < … $`          | `<subscript> → num`                                   |
| 188 | `$ } <stmts> } <stmts> ; <assign_end> = ] num`                           | `0 ] = i ; } if ( 1 < … $`          | совпадение '0'                                        |
| 189 | `$ } <stmts> } <stmts> ; <assign_end> = ]`                               | `] = i ; } if ( 1 < a … $`          | совпадение ']'                                        |
| 190 | `$ } <stmts> } <stmts> ; <assign_end> =`                                 | `= i ; } if ( 1 < a [ … $`          | совпадение '='                                        |
| 191 | `$ } <stmts> } <stmts> ; <assign_end>`                                   | `i ; } if ( 1 < a [ 2 … $`          | `<assign_end> → id <index>`                           |
| 192 | `$ } <stmts> } <stmts> ; <index> id`                                     | `i ; } if ( 1 < a [ 2 … $`          | совпадение 'i'                                        |
| 193 | `$ } <stmts> } <stmts> ; <index>`                                        | `; } if ( 1 < a [ 2 ] … $`          | `<index> → ε`                                         |
| 194 | `$ } <stmts> } <stmts> ;`                                                | `; } if ( 1 < a [ 2 ] … $`          | совпадение ';'                                        |
| 195 | `$ } <stmts> } <stmts>`                                                  | `} if ( 1 < a [ 2 ] ) … $`          | `<stmts> → ε`                                         |
| 196 | `$ } <stmts> }`                                                          | `} if ( 1 < a [ 2 ] ) … $`          | совпадение '}'                                        |
| 197 | `$ } <stmts>`                                                            | `if ( 1 < a [ 2 ] ) return … $`     | `<stmts> → <statement> <stmts>`                       |
| 198 | `$ } <stmts> <statement>`                                                | `if ( 1 < a [ 2 ] ) return … $`     | `<statement> → <if> <statement>`                      |
| 199 | `$ } <stmts> <statement> <if>`                                           | `if ( 1 < a [ 2 ] ) return … $`     | `<if> → if ( <bool_expression> )`                     |
| 200 | `$ } <stmts> <statement> ) <bool_expression> ( if`                       | `if ( 1 < a [ 2 ] ) return … $`     | совпадение 'if'                                       |
| 201 | `$ } <stmts> <statement> ) <bool_expression> (`                          | `( 1 < a [ 2 ] ) return 1 … $`      | совпадение '('                                        |
| 202 | `$ } <stmts> <statement> ) <bool_expression>`                            | `1 < a [ 2 ] ) return 1 ; … $`      | `<bool_expression> → num <relop> id <index>`          |
| 203 | `$ } <stmts> <statement> ) <index> id <relop> num`                       | `1 < a [ 2 ] ) return 1 ; … $`      | совпадение '1'                                        |
| 204 | `$ } <stmts> <statement> ) <index> id <relop>`                           | `< a [ 2 ] ) return 1 ; return … $` | `<relop> → <`                                         |
| 205 | `$ } <stmts> <statement> ) <index> id <`                                 | `< a [ 2 ] ) return 1 ; return … $` | совпадение '<'                                        |
| 206 | `$ } <stmts> <statement> ) <index> id`                                   | `a [ 2 ] ) return 1 ; return 2 … $` | совпадение 'a'                                        |
| 207 | `$ } <stmts> <statement> ) <index>`                                      | `[ 2 ] ) return 1 ; return 2 ; … $` | `<index> → [ <subscript> ]`                           |
| 208 | `$ } <stmts> <statement> ) ] <subscript> [`                              | `[ 2 ] ) return 1 ; return 2 ; … $` | совпадение '['                                        |
| 209 | `$ } <stmts> <statement> ) ] <subscript>`                                | `2 ] ) return 1 ; return 2 ; } $`   | `<subscript> → num`                                   |
| 210 | `$ } <stmts> <statement> ) ] num`                                        | `2 ] ) return 1 ; return 2 ; } $`   | совпадение '2'                                        |
| 211 | `$ } <stmts> <statement> ) ]`                                            | `] ) return 1 ; return 2 ; } $`     | совпадение ']'                                        |
| 212 | `$ } <stmts> <statement> )`                                              | `) return 1 ; return 2 ; } $`       | совпадение ')'                                        |
| 213 | `$ } <stmts> <statement>`                                                | `return 1 ; return 2 ; } $`         | `<statement> → <return>`                              |
| 214 | `$ } <stmts> <return>`                                                   | `return 1 ; return 2 ; } $`         | `<return> → return num ;`                             |
| 215 | `$ } <stmts> ; num return`                                               | `return 1 ; return 2 ; } $`         | совпадение 'return'                                   |
| 216 | `$ } <stmts> ; num`                                                      | `1 ; return 2 ; } $`                | совпадение '1'                                        |
| 217 | `$ } <stmts> ;`                                                          | `; return 2 ; } $`                  | совпадение ';'                                        |
| 218 | `$ } <stmts>`                                                            | `return 2 ; } $`                    | `<stmts> → <statement> <stmts>`                       |
| 219 | `$ } <stmts> <statement>`                                                | `return 2 ; } $`                    | `<statement> → <return>`                              |
| 220 | `$ } <stmts> <return>`                                                   | `return 2 ; } $`                    | `<return> → return num ;`                             |
| 221 | `$ } <stmts> ; num return`                                               | `return 2 ; } $`                    | совпадение 'return'                                   |
| 222 | `$ } <stmts> ; num`                                                      | `2 ; } $`                           | совпадение '2'                                        |
| 223 | `$ } <stmts> ;`                                                          | `; } $`                             | совпадение ';'                                        |
| 224 | `$ } <stmts>`                                                            | `} $`                               | `<stmts> → ε`                                         |
| 225 | `$ }`                                                                    | `} $`                               | совпадение '}'                                        |
| 226 | `$`                                                                      | `$`                                 | Разбор завершён, ошибок нет                           |
