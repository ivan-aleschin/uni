# Ход разбора: ok_decl.cl

Грамматика: из методички, восстановление: режим фразы.

## Исходный текст

```c
// Вложенные блоки и объявление с инициализацией идентификатором.
// ожидается: panic=0 phrase=0
void main() {
    {
        {
            int answer = other_value;
        }
    }
}
```

## Ошибки (0)

Ошибок нет.

## Таблица разбора

Стек: дно `$` слева, вершина справа. Вход: текущий токен первый, длинный хвост сокращён до 10 токенов.

| №   | Стек                                | Вход                                          | Примечание                                    |
|-----|-------------------------------------|-----------------------------------------------|-----------------------------------------------|
| 1   | `$ <program>`                       | `void main ( ) { { { int answer = … $`        | `<program> → <type> main ( ) { <statement> }` |
| 2   | `$ } <statement> { ) ( main <type>` | `void main ( ) { { { int answer = … $`        | `<type> → void`                               |
| 3   | `$ } <statement> { ) ( main void`   | `void main ( ) { { { int answer = … $`        | совпадение 'void'                             |
| 4   | `$ } <statement> { ) ( main`        | `main ( ) { { { int answer = other_value … $` | совпадение 'main'                             |
| 5   | `$ } <statement> { ) (`             | `( ) { { { int answer = other_value ; … $`    | совпадение '('                                |
| 6   | `$ } <statement> { )`               | `) { { { int answer = other_value ; } … $`    | совпадение ')'                                |
| 7   | `$ } <statement> {`                 | `{ { { int answer = other_value ; } } … $`    | совпадение '{'                                |
| 8   | `$ } <statement>`                   | `{ { int answer = other_value ; } } } $`      | `<statement> → { <statement> }`               |
| 9   | `$ } } <statement> {`               | `{ { int answer = other_value ; } } } $`      | совпадение '{'                                |
| 10  | `$ } } <statement>`                 | `{ int answer = other_value ; } } } $`        | `<statement> → { <statement> }`               |
| 11  | `$ } } } <statement> {`             | `{ int answer = other_value ; } } } $`        | совпадение '{'                                |
| 12  | `$ } } } <statement>`               | `int answer = other_value ; } } } $`          | `<statement> → <declaration> ;`               |
| 13  | `$ } } } ; <declaration>`           | `int answer = other_value ; } } } $`          | `<declaration> → <type> id <assign>`          |
| 14  | `$ } } } ; <assign> id <type>`      | `int answer = other_value ; } } } $`          | `<type> → int`                                |
| 15  | `$ } } } ; <assign> id int`         | `int answer = other_value ; } } } $`          | совпадение 'int'                              |
| 16  | `$ } } } ; <assign> id`             | `answer = other_value ; } } } $`              | совпадение 'answer'                           |
| 17  | `$ } } } ; <assign>`                | `= other_value ; } } } $`                     | `<assign> → = <assign_end>`                   |
| 18  | `$ } } } ; <assign_end> =`          | `= other_value ; } } } $`                     | совпадение '='                                |
| 19  | `$ } } } ; <assign_end>`            | `other_value ; } } } $`                       | `<assign_end> → id`                           |
| 20  | `$ } } } ; id`                      | `other_value ; } } } $`                       | совпадение 'other_value'                      |
| 21  | `$ } } } ;`                         | `; } } } $`                                   | совпадение ';'                                |
| 22  | `$ } } }`                           | `} } } $`                                     | совпадение '}'                                |
| 23  | `$ } }`                             | `} } $`                                       | совпадение '}'                                |
| 24  | `$ }`                               | `} $`                                         | совпадение '}'                                |
| 25  | `$`                                 | `$`                                           | Разбор завершён, ошибок нет                   |
