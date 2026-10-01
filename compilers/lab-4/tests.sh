#!/usr/bin/env bash
# Прогон всех примеров из examples/ в обоих режимах восстановления.
# В начале каждого примера записано, сколько ошибок должно найтись:
#   // ожидается: panic=N phrase=M
#   // флаги: --ext            (необязательно)
# Таблицы хода разбора складываются в results/.
cd "$(dirname "$0")" || exit 2
pass=0
fail=0
for f in examples/*.cl; do
    flags=$(sed -n 's|^// флаги: ||p' "$f")
    for mode in panic phrase; do
        want=$(sed -n "s|^// ожидается:.*$mode=\([0-9]*\).*|\1|p" "$f")
        extra=""
        [ "$mode" = phrase ] && extra="--phrase"
        # shellcheck disable=SC2086
        got=$(./lab4 $flags $extra --out results "$f" | sed -n 's/^Итого ошибок: \([0-9]*\).*/\1/p')
        if [ "$got" = "$want" ]; then
            pass=$((pass + 1))
            printf '  ok    %-24s %-6s ошибок: %s\n' "$f" "$mode" "$got"
        else
            fail=$((fail + 1))
            printf '  FAIL  %-24s %-6s ошибок: %s, ожидалось: %s\n' "$f" "$mode" "$got" "$want"
        fi
    done
done
# Обе грамматики должны быть LL(1) (в таблице нет ячеек с двумя продукциями).
for g in "" --ext; do
    # shellcheck disable=SC2086
    if ./lab4 --table $g --out results | grep -q "конфликтов нет"; then
        pass=$((pass + 1)); echo "  ok    грамматика ${g:-из методички} — LL(1)"
    else
        fail=$((fail + 1)); echo "  FAIL  грамматика ${g:-из методички} не LL(1)"
    fi
done
echo "Пройдено: $pass, не пройдено: $fail"
[ "$fail" -eq 0 ]
