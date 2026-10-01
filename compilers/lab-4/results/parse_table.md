# Таблица предиктивного анализа C-light

Сгенерировано программой ЛР4 (`main.py`) по грамматике
из `grammar.py`.
Нетерминалы — в угловых скобках, `id` и `num` — токены лексера (`<identifier>` и `<number>`).

## Продукции

```
 1. <program> → <type> main ( ) { <statement> }
 2. <type> → int
 3. <type> → bool
 4. <type> → void
 5. <statement> → ε
 6. <statement> → <declaration> ;
 7. <statement> → { <statement> }
 8. <statement> → <for> <statement>
 9. <statement> → <if> <statement>
10. <statement> → <return>
11. <declaration> → <type> id <assign>
12. <assign> → ε
13. <assign> → = <assign_end>
14. <assign_end> → id
15. <assign_end> → num
16. <for> → for ( <declaration> ; <bool_expression> ; )
17. <bool_expression> → id <relop> id
18. <bool_expression> → num <relop> id
19. <relop> → <
20. <relop> → >
21. <relop> → ==
22. <relop> → !=
23. <if> → if ( <bool_expression> )
24. <return> → return num ;
```

## FIRST, FOLLOW и синхронизирующие множества

| Нетерминал          | FIRST                             | FOLLOW                            | synch (режим паники)                        |
|---------------------|-----------------------------------|-----------------------------------|---------------------------------------------|
| `<program>`         | `int bool void`                   | `$`                               | `$`                                         |
| `<type>`            | `int bool void`                   | `main id`                         | `int bool void main for if return { } id $` |
| `<statement>`       | `int bool void for if return { ε` | `}`                               | `} $`                                       |
| `<declaration>`     | `int bool void`                   | `;`                               | `int bool void for if return { } ; $`       |
| `<assign>`          | `= ε`                             | `;`                               | `int bool void for if return { } ; $`       |
| `<assign_end>`      | `id num`                          | `;`                               | `int bool void for if return { } ; $`       |
| `<for>`             | `for`                             | `int bool void for if return { }` | `int bool void for if return { } $`         |
| `<bool_expression>` | `id num`                          | `) ;`                             | `int bool void for if return ) { } ; $`     |
| `<relop>`           | `< > == !=`                       | `id`                              | `int bool void for if return { } id $`      |
| `<if>`              | `if`                              | `int bool void for if return { }` | `int bool void for if return { } $`         |
| `<return>`          | `return`                          | `}`                               | `int bool void for if return { } $`         |

## Таблица M[A, a]

В ячейке — номер продукции из списка выше; `synch` — синхронизирующий символ (при ошибке нетерминал снимается со стека); пустая ячейка — ошибка, входной символ пропускается; `(k)` — ошибка, но у нетерминала единственная продукция k, начинающаяся с `<type>`; она раскрывается по умолчанию, и ошибку сообщает уже `<type>`.

| A \ a               | `int` | `bool` | `void` | `main` | `for` | `if`  | `return` | `(`  | `)`   | `{`   | `}`   | `;`   | `=`  | `<`  | `>`  | `==` | `!=` | `id`  | `num` | `$`   |
|---------------------|-------|--------|--------|--------|-------|-------|----------|------|-------|-------|-------|-------|------|------|------|------|------|-------|-------|-------|
| `<program>`         | 1     | 1      | 1      | (1)    | (1)   | (1)   | (1)      | (1)  | (1)   | (1)   | (1)   | (1)   | (1)  | (1)  | (1)  | (1)  | (1)  | (1)   | (1)   | synch |
| `<type>`            | 2     | 3      | 4      | synch  | synch | synch | synch    |      |       | synch | synch |       |      |      |      |      |      | synch |       | synch |
| `<statement>`       | 6     | 6      | 6      |        | 8     | 9     | 10       |      |       | 7     | 5     |       |      |      |      |      |      |       |       | synch |
| `<declaration>`     | 11    | 11     | 11     | (11)   | synch | synch | synch    | (11) | (11)  | synch | synch | synch | (11) | (11) | (11) | (11) | (11) | (11)  | (11)  | synch |
| `<assign>`          | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | 12    | 13   |      |      |      |      |       |       | synch |
| `<assign_end>`      | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch | synch |      |      |      |      |      | 14    | 15    | synch |
| `<for>`             | synch | synch  | synch  |        | 16    | synch | synch    |      |       | synch | synch |       |      |      |      |      |      |       |       | synch |
| `<bool_expression>` | synch | synch  | synch  |        | synch | synch | synch    |      | synch | synch | synch | synch |      |      |      |      |      | 17    | 18    | synch |
| `<relop>`           | synch | synch  | synch  |        | synch | synch | synch    |      |       | synch | synch |       |      | 19   | 20   | 21   | 22   | synch |       | synch |
| `<if>`              | synch | synch  | synch  |        | synch | 23    | synch    |      |       | synch | synch |       |      |      |      |      |      |       |       | synch |
| `<return>`          | synch | synch  | synch  |        | synch | synch | 24       |      |       | synch | synch |       |      |      |      |      |      |       |       | synch |

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
