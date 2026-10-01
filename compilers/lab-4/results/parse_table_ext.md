# Таблица предиктивного анализа C-light (расширенная грамматика, --ext)

Сгенерировано программой ЛР4 (`cpp/lab4` или `python/main.py`, вывод одинаковый) по грамматике
из `cpp/grammar.hpp` (`python/grammar.py`).
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
13. <declaration> → <type> id <assign>
14. <assign> → ε
15. <assign> → = <assign_end>
16. <assign_end> → id
17. <assign_end> → num
18. <for> → for ( <declaration> ; <bool_expression> ; )
19. <bool_expression> → id <relop> id
20. <bool_expression> → num <relop> id
21. <relop> → <
22. <relop> → >
23. <relop> → ==
24. <relop> → !=
25. <if> → if ( <bool_expression> )
26. <return> → return num ;
```

## FIRST, FOLLOW и синхронизирующие множества

| Нетерминал          | FIRST                               | FOLLOW                              | synch (режим паники)                          |
|---------------------|-------------------------------------|-------------------------------------|-----------------------------------------------|
| `<program>`         | `int bool void`                     | `$`                                 | `$`                                           |
| `<type>`            | `int bool void`                     | `main id`                           | `int bool void main for if return { } ; id $` |
| `<stmts>`           | `int bool void for if return { ; ε` | `}`                                 | `} $`                                         |
| `<statement>`       | `int bool void for if return { ;`   | `int bool void for if return { } ;` | `int bool void for if return { } ; $`         |
| `<declaration>`     | `int bool void`                     | `;`                                 | `int bool void for if return { } ; $`         |
| `<assign>`          | `= ε`                               | `;`                                 | `int bool void for if return { } ; $`         |
| `<assign_end>`      | `id num`                            | `;`                                 | `int bool void for if return { } ; $`         |
| `<for>`             | `for`                               | `int bool void for if return { ;`   | `int bool void for if return { } ; $`         |
| `<bool_expression>` | `id num`                            | `) ;`                               | `int bool void for if return ) { } ; $`       |
| `<relop>`           | `< > == !=`                         | `id`                                | `int bool void for if return { } ; id $`      |
| `<if>`              | `if`                                | `int bool void for if return { ;`   | `int bool void for if return { } ; $`         |
| `<return>`          | `return`                            | `int bool void for if return { } ;` | `int bool void for if return { } ; $`         |

## Таблица M[A, a]

В ячейке — номер продукции из списка выше; `synch` — синхронизирующий символ (при ошибке нетерминал снимается со стека); пустая ячейка — ошибка, входной символ пропускается; `(k)` — ошибка, но у нетерминала единственная продукция k, начинающаяся с `<type>`; она раскрывается по умолчанию, и ошибку сообщает уже `<type>`.

| A \ a               | `int` | `bool` | `void` | `main` | `for` | `if`  | `return` | `(`  | `)`   | `{`   | `}`   | `;`   | `=`  | `<`  | `>`  | `==` | `!=` | `id`  | `num` | `$`   |
|---------------------|-------|--------|--------|--------|-------|-------|----------|------|-------|-------|-------|-------|------|------|------|------|------|-------|-------|-------|
| `<program>`         | 1     | 1      | 1      | (1)    | (1)   | (1)   | (1)      | (1)  | (1)   | (1)   | (1)   | (1)   | (1)  | (1)  | (1)  | (1)  | (1)  | (1)   | (1)   | synch |
| `<type>`            | 2     | 3      | 4      | synch  | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      | synch |       | synch |
| `<stmts>`           | 5     | 5      | 5      |        | 5     | 5     | 5        |      |       | 5     | 6     | 5     |      |      |      |      |      |       |       | synch |
| `<statement>`       | 7     | 7      | 7      |        | 9     | 10    | 11       |      |       | 8     | synch | 12    |      |      |      |      |      |       |       | synch |
| `<declaration>`     | 13    | 13     | 13     | (13)   | synch | synch | synch    | (13) | (13)  | synch | synch | synch | (13) | (13) | (13) | (13) | (13) | (13)  | (13)  | synch |
| `<assign>`          | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | 14    | 15   |      |      |      |      |       |       | synch |
| `<assign_end>`      | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      | 16    | 17    | synch |
| `<for>`             | synch | synch  | synch  |        | 18    | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      |       |       | synch |
| `<bool_expression>` | synch | synch  | synch  |        | synch | synch | synch    |      | synch | synch | synch | synch |      |      |      |      |      | 19    | 20    | synch |
| `<relop>`           | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      | 21   | 22   | 23   | 24   | synch |       | synch |
| `<if>`              | synch | synch  | synch  |        | synch | 25    | synch    |      |       | synch | synch | synch |      |      |      |      |      |       |       | synch |
| `<return>`          | synch | synch  | synch  |        | synch | synch | 26       |      |       | synch | synch | synch |      |      |      |      |      |       |       | synch |

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
