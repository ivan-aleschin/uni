#!/usr/bin/env bash
# Прогон всех примеров из examples/ в обоих режимах восстановления.
# В начале каждого примера записано, сколько ошибок должно найтись:
#   // ожидается: panic=N phrase=M
#   // флаги: --ext            (необязательно)
# Для каждого запуска проверяется, что число ошибок совпадает с ожидаемым.
# Таблицы хода разбора складываются в results/.
cd "$(dirname "$0")" || exit 2
prog=(python3 main.py)
pass=0
fail=0

# check ФАЙЛ РЕЖИМ ОЖИДАЕМОЕ АРГУМЕНТЫ... — запускает анализатор и сверяет число ошибок.
check() {
    local name=$1 mode=$2 want=$3
    shift 3
    local got
    got=$("${prog[@]}" "$@" --out results | sed -n 's/^Итого ошибок: \([0-9]*\).*/\1/p')
    if [ "$got" = "$want" ]; then
        pass=$((pass + 1))
        printf '  ok    %-24s %-6s ошибок: %s\n' "$name" "$mode" "$got"
    else
        fail=$((fail + 1))
        printf '  FAIL  %-24s %-6s ошибок: %s, ожидалось: %s\n' "$name" "$mode" "$got" "$want"
    fi
}

for f in examples/*.cl; do
    flags=$(sed -n 's|^// флаги: ||p' "$f")
    for mode in panic phrase; do
        want=$(sed -n "s|^// ожидается:.*$mode=\([0-9]*\).*|\1|p" "$f")
        extra=""
        [ "$mode" = phrase ] && extra="--phrase"
        # shellcheck disable=SC2086
        check "$f" "$mode" "$want" $flags $extra "$f"
    done
done

# Обе грамматики должны быть LL(1): в таблице нет ячеек с двумя продукциями.
for g in "" --ext; do
    # shellcheck disable=SC2086
    if "${prog[@]}" --table $g --out results | grep -q "конфликтов нет"; then
        pass=$((pass + 1)); echo "  ok    грамматика ${g:-из методички} — LL(1)"
    else
        fail=$((fail + 1)); echo "  FAIL  грамматика ${g:-из методички} — есть конфликты"
    fi
done
echo "Пройдено: $pass, не пройдено: $fail"
[ "$fail" -eq 0 ]
