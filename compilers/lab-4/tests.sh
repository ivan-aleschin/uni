#!/usr/bin/env bash
# Прогон примеров в обоих режимах восстановления.
#   bash tests.sh                  — все примеры: examples/ и examples/arrays/
#   bash tests.sh examples/arrays  — только примеры из указанных папок (здесь — массивы)
# В начале каждого примера записано, сколько ошибок должно найтись:
#   // ожидается: panic=N phrase=M
#   // флаги: --ext или --arrays   (необязательно)
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
        printf '  ok    %-32s %-6s ошибок: %s\n' "$name" "$mode" "$got"
    else
        fail=$((fail + 1))
        printf '  FAIL  %-32s %-6s ошибок: %s, ожидалось: %s\n' "$name" "$mode" "$got" "$want"
    fi
}

dirs=("$@")
[ ${#dirs[@]} -eq 0 ] && dirs=(examples examples/arrays)
files=()
for d in "${dirs[@]}"; do files+=("$d"/*.cl); done
for f in "${files[@]}"; do
    if [ ! -f "$f" ]; then  # пустая или несуществующая папка: glob остался как есть
        fail=$((fail + 1)); echo "  FAIL  нет примеров: $f"; continue
    fi
    flags=$(sed -n 's|^// флаги: ||p' "$f")
    for mode in panic phrase; do
        want=$(sed -n "s|^// ожидается:.*$mode=\([0-9]*\).*|\1|p" "$f")
        extra=""
        [ "$mode" = phrase ] && extra="--phrase"
        # shellcheck disable=SC2086
        check "$f" "$mode" "$want" $flags $extra "$f"
    done
done

# Все три грамматики должны быть LL(1): в таблице нет ячеек с двумя продукциями.
for g in "" --ext --arrays; do
    # shellcheck disable=SC2086
    if "${prog[@]}" --table $g --out results | grep -q "конфликтов нет"; then
        pass=$((pass + 1)); echo "  ok    грамматика ${g:-из методички} — LL(1)"
    else
        fail=$((fail + 1)); echo "  FAIL  грамматика ${g:-из методички} — есть конфликты"
    fi
done
echo "Пройдено: $pass, не пройдено: $fail"
[ "$fail" -eq 0 ]
