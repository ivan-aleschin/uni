#!/usr/bin/env bash
# Прогон всех примеров из examples/ в обоих режимах восстановления для обеих
# реализаций: C++ (cpp/lab4) и Python (python/main.py).
# В начале каждого примера записано, сколько ошибок должно найтись:
#   // ожидается: panic=N phrase=M
#   // флаги: --ext            (необязательно)
# Для каждого запуска проверяется:
#   - число ошибок у C++ и у Python совпадает с ожидаемым;
#   - вывод в консоль и файл хода разбора у двух версий совпадают байт в байт.
# Таблицы хода разбора складываются в results/ (их пишут обе версии, одинаково).
cd "$(dirname "$0")" || exit 2
make -s -C cpp lab4 || exit 2
cpp=(./cpp/lab4)
py=(python3 python/main.py)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
pass=0
fail=0

# check ФАЙЛ РЕЖИМ ОЖИДАЕМОЕ ФАЙЛ_ТАБЛИЦЫ АРГУМЕНТЫ... — запускает обе версии и сравнивает.
check() {
    local name=$1 mode=$2 want=$3 file=$4
    shift 4
    "${cpp[@]}" "$@" --out results >"$tmp/cpp.out"
    cp "$file" "$tmp/cpp.md"
    "${py[@]}" "$@" --out results >"$tmp/py.out"
    local got_cpp got_py same=yes
    got_cpp=$(sed -n 's/^Итого ошибок: \([0-9]*\).*/\1/p' "$tmp/cpp.out")
    got_py=$(sed -n 's/^Итого ошибок: \([0-9]*\).*/\1/p' "$tmp/py.out")
    cmp -s "$tmp/cpp.out" "$tmp/py.out" && cmp -s "$tmp/cpp.md" "$file" || same=no
    if [ "$got_cpp" = "$want" ] && [ "$got_py" = "$want" ] && [ $same = yes ]; then
        pass=$((pass + 1))
        printf '  ok    %-24s %-6s ошибок: %s, вывод C++ = Python\n' "$name" "$mode" "$got_cpp"
    else
        fail=$((fail + 1))
        printf '  FAIL  %-24s %-6s ошибок: C++ %s, Python %s, ожидалось: %s; вывод совпадает: %s\n' \
            "$name" "$mode" "$got_cpp" "$got_py" "$want" "$same"
    fi
}

for f in examples/*.cl; do
    flags=$(sed -n 's|^// флаги: ||p' "$f")
    stem=$(basename "$f" .cl)
    for mode in panic phrase; do
        want=$(sed -n "s|^// ожидается:.*$mode=\([0-9]*\).*|\1|p" "$f")
        extra="" suffix=".trace.md"
        [ "$mode" = phrase ] && extra="--phrase" suffix=".phrase.trace.md"
        # shellcheck disable=SC2086
        check "$f" "$mode" "$want" "results/$stem$suffix" $flags $extra "$f"
    done
done

# Обе грамматики должны быть LL(1) (в таблице нет ячеек с двумя продукциями),
# и таблицу M обе версии строят одинаково.
for g in "" --ext; do
    file=results/parse_table${g:+_ext}.md
    # shellcheck disable=SC2086
    ok_cpp=$("${cpp[@]}" --table $g --out results | grep -c "конфликтов нет")
    cp "$file" "$tmp/cpp.md"
    # shellcheck disable=SC2086
    ok_py=$("${py[@]}" --table $g --out results | grep -c "конфликтов нет")
    if [ "$ok_cpp" = 1 ] && [ "$ok_py" = 1 ] && cmp -s "$tmp/cpp.md" "$file"; then
        pass=$((pass + 1)); echo "  ok    грамматика ${g:-из методички} — LL(1), таблица C++ = Python"
    else
        fail=$((fail + 1)); echo "  FAIL  грамматика ${g:-из методички}: LL(1) C++ $ok_cpp, Python $ok_py или таблицы различаются"
    fi
done
echo "Пройдено: $pass, не пройдено: $fail"
[ "$fail" -eq 0 ]
