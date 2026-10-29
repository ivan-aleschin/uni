# Таблица предиктивного анализа C-light (массивы, --arrays)

Сгенерировано программой ЛР4 (`main.py`) по грамматике
из `grammar.py`.
Нетерминалы — в угловых скобках, `id` и `num` — токены лексера (`<identifier>` и `<number>`).

## Продукции

```
 1. <program> → <type> main ( ) { <stmts> }
 2. <type> → int
 3. <type> → bool
 4. <type> → void
 5. <stmts> → <statement> <stmts>
 6. <stmts> → ε
 7. <statement> → <declaration> ;
 8. <statement> → { <stmts> }
 9. <statement> → <for> <statement>
10. <statement> → <if> <statement>
11. <statement> → <return>
12. <statement> → ;
13. <statement> → id <index> = <assign_end> ;
14. <declaration> → <type> id <decl_tail>
15. <assign> → ε
16. <assign> → = <assign_end>
17. <assign_end> → id <index>
18. <assign_end> → num
19. <for> → for ( <declaration> ; <bool_expression> ; )
20. <bool_expression> → id <index> <relop> id <index>
21. <bool_expression> → num <relop> id <index>
22. <relop> → <
23. <relop> → >
24. <relop> → ==
25. <relop> → !=
26. <if> → if ( <bool_expression> )
27. <return> → return num ;
28. <decl_tail> → <assign>
29. <decl_tail> → [ <size> ] <array_init>
30. <size> → num
31. <size> → ε
32. <array_init> → ε
33. <array_init> → = { <init_list> }
34. <init_list> → <assign_end> <init_rest>
35. <init_rest> → , <assign_end> <init_rest>
36. <init_rest> → ε
37. <index> → ε
38. <index> → [ <subscript> ]
39. <subscript> → id
40. <subscript> → num
```

## FIRST, FOLLOW и синхронизирующие множества

| Нетерминал          | FIRST                                  | FOLLOW                                 | synch (режим паники)                                     |
|---------------------|----------------------------------------|----------------------------------------|----------------------------------------------------------|
| `<program>`         | `int bool void`                        | `$`                                    | `$`                                                      |
| `<type>`            | `int bool void`                        | `main id`                              | `int bool void main for if return { } ; id $`            |
| `<stmts>`           | `int bool void for if return { ; id ε` | `}`                                    | `} $`                                                    |
| `<statement>`       | `int bool void for if return { ; id`   | `int bool void for if return { } ; id` | `int bool void for if return { } ; id $`                 |
| `<declaration>`     | `int bool void`                        | `;`                                    | `int bool void for if return { } ; id $`                 |
| `<assign>`          | `= ε`                                  | `;`                                    | `int bool void for if return { } ; id $`                 |
| `<assign_end>`      | `id num`                               | `} ; ,`                                | `int bool void for if return { } ; , id $`               |
| `<for>`             | `for`                                  | `int bool void for if return { ; id`   | `int bool void for if return { } ; id $`                 |
| `<bool_expression>` | `id num`                               | `) ;`                                  | `int bool void for if return ) { } ; id $`               |
| `<relop>`           | `< > == !=`                            | `id`                                   | `int bool void for if return { } ; id $`                 |
| `<if>`              | `if`                                   | `int bool void for if return { ; id`   | `int bool void for if return { } ; id $`                 |
| `<return>`          | `return`                               | `int bool void for if return { } ; id` | `int bool void for if return { } ; id $`                 |
| `<decl_tail>`       | `= [ ε`                                | `;`                                    | `int bool void for if return { } ; id $`                 |
| `<size>`            | `num ε`                                | `]`                                    | `int bool void for if return { } ; ] id $`               |
| `<array_init>`      | `= ε`                                  | `;`                                    | `int bool void for if return { } ; id $`                 |
| `<init_list>`       | `id num`                               | `}`                                    | `int bool void for if return { } ; id $`                 |
| `<init_rest>`       | `, ε`                                  | `}`                                    | `int bool void for if return { } ; id $`                 |
| `<index>`           | `[ ε`                                  | `) } ; = < > == != ,`                  | `int bool void for if return ) { } ; = < > == != , id $` |
| `<subscript>`       | `id num`                               | `]`                                    | `int bool void for if return { } ; ] id $`               |

## Таблица M[A, a]

В ячейке — номер продукции из списка выше; `synch` — синхронизирующий символ (при ошибке нетерминал снимается со стека); пустая ячейка — ошибка, входной символ пропускается; `(k)` — ошибка, но у нетерминала единственная продукция k, начинающаяся с `<type>`; она раскрывается по умолчанию, и ошибку сообщает уже `<type>`.

| A \ a               | `int` | `bool` | `void` | `main` | `for` | `if`  | `return` | `(`  | `)`   | `{`   | `}`   | `;`   | `=`  | `<`  | `>`  | `==` | `!=` | `[`  | `]`   | `,`   | `id`  | `num` | `$`   |
|---------------------|-------|--------|--------|--------|-------|-------|----------|------|-------|-------|-------|-------|------|------|------|------|------|------|-------|-------|-------|-------|-------|
| `<program>`         | 1     | 1      | 1      | (1)    | (1)   | (1)   | (1)      | (1)  | (1)   | (1)   | (1)   | (1)   | (1)  | (1)  | (1)  | (1)  | (1)  | (1)  | (1)   | (1)   | (1)   | (1)   | synch |
| `<type>`            | 2     | 3      | 4      | synch  | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |      |       |       | synch |       | synch |
| `<stmts>`           | 5     | 5      | 5      |        | 5     | 5     | 5        |      |       | 5     | 6     | 5     |      |      |      |      |      |      |       |       | 5     |       | synch |
| `<statement>`       | 7     | 7      | 7      |        | 9     | 10    | 11       |      |       | 8     | synch | 12    |      |      |      |      |      |      |       |       | 13    |       | synch |
| `<declaration>`     | 14    | 14     | 14     | (14)   | synch | synch | synch    | (14) | (14)  | synch | synch | synch | (14) | (14) | (14) | (14) | (14) | (14) | (14)  | (14)  | synch | (14)  | synch |
| `<assign>`          | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | 15    | 16   |      |      |      |      |      |       |       | synch |       | synch |
| `<assign_end>`      | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |      |       | synch | 17    | 18    | synch |
| `<for>`             | synch | synch  | synch  |        | 19    | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |      |       |       | synch |       | synch |
| `<bool_expression>` | synch | synch  | synch  |        | synch | synch | synch    |      | synch | synch | synch | synch |      |      |      |      |      |      |       |       | 20    | 21    | synch |
| `<relop>`           | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      | 22   | 23   | 24   | 25   |      |       |       | synch |       | synch |
| `<if>`              | synch | synch  | synch  |        | synch | 26    | synch    |      |       | synch | synch | synch |      |      |      |      |      |      |       |       | synch |       | synch |
| `<return>`          | synch | synch  | synch  |        | synch | synch | 27       |      |       | synch | synch | synch |      |      |      |      |      |      |       |       | synch |       | synch |
| `<decl_tail>`       | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | 28    | 28   |      |      |      |      | 29   |       |       | synch |       | synch |
| `<size>`            | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |      | 31    |       | synch | 30    | synch |
| `<array_init>`      | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | 32    | 33   |      |      |      |      |      |       |       | synch |       | synch |
| `<init_list>`       | synch | synch  | synch  | (34)   | synch | synch | synch    | (34) | (34)  | synch | synch | synch | (34) | (34) | (34) | (34) | (34) | (34) | (34)  | (34)  | 34    | 34    | synch |
| `<init_rest>`       | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | 36    | synch |      |      |      |      |      |      |       | 35    | synch |       | synch |
| `<index>`           | synch | synch  | synch  |        | synch | synch | synch    |      | 37    | synch | 37    | 37    | 37   | 37   | 37   | 37   | 37   | 38   |       | 37    | synch |       | synch |
| `<subscript>`       | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |      | synch |       | 39    | 40    | synch |

## Проверка LL(1)

Ни в одной ячейке нет двух продукций — грамматика LL(1).

## Режим фразы (--phrase)

Ошибочные ячейки (пустые и synch) обрабатываются процедурами (проверяются по порядку):

1. `M[<relop>, =]` — замена `=` на `==`;
2. `M[<type>, id]`, если за ним снова id, — неизвестный тип, считаем его типом;
3. `M[<statement>, id]` (и `M[<stmts>, id]`): если за id идёт `=` или `;` — объявление без типа,
   если ещё один id — неизвестный тип; дальше разбираем как `id <assign> ;`;
4. если следующий токен b подходит (`M[A, b]` не пусто) — текущий токен лишний, удаляем его;
5. иначе — как в режиме паники (synch → снять A, пусто → пропустить токен).

Несовпадение терминала t на вершине с токеном a: удаление a (если за ним идёт t), вставка t
(если a может идти после t), замена a на t (если следующий токен может идти после t), иначе паника.
