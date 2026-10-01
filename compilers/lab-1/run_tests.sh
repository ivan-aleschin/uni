#!/usr/bin/env bash
# Прогоняет каждую строку tests.txt через калькулятор и сверяет вывод с ожиданием.
#
#   ./run_tests.sh              тесты для python3 main.py
#   ./run_tests.sh <команда…>   любая команда, читающая выражения со stdin
cd "$(dirname "$0")"

PROG=(python3 main.py)

# run_suite <название> <команда…> — один прогон tests.txt, код возврата 0, если всё прошло
run_suite() {
    local name="$1"
    shift
    local pass=0 fail=0 line expr expected output want ok
    echo "=== $name: $* ==="
    while IFS= read -r line; do
        [[ -z "${line// }" || "$line" == \#* ]] && continue
        expr="${line%|*}"
        expected="${line##*|}"
        # хвостовые пробелы выражения не срезаем: калькулятор их и так пропускает,
        # а строка из одних пробелов нужна для теста "пустое выражение"
        expected="$(echo "$expected" | sed 's/^ *//; s/ *$//')"

        output="$(printf '%s\n' "$expr" | "$@")"
        if [[ "$expected" == '!'* ]]; then
            want="${expected#! }"
            grep -qF -- "$want" <<< "$output" && ok=1 || ok=0
        else
            want="Результат: $expected"
            grep -qxF -- "$want" <<< "$output" && ok=1 || ok=0
        fi

        if (( ok )); then
            pass=$((pass + 1))
            printf 'OK    %s -> %s\n' "$expr" "$expected"
        else
            fail=$((fail + 1))
            printf 'FAIL  %s ждали: %s\n%s\n' "$expr" "$expected" "$output"
        fi
    done < tests.txt

    echo "$name — пройдено: $pass, провалено: $fail"
    (( fail == 0 ))
}

if (( $# )); then
    run_suite "$1" "$@"
else
    run_suite "main.py" "${PROG[@]}"
fi
