#!/usr/bin/env bash
# Прогоняет каждую строку tests.txt через ./lab1 и сверяет вывод с ожиданием.
cd "$(dirname "$0")"

pass=0
fail=0
while IFS= read -r line; do
    [[ -z "${line// }" || "$line" == \#* ]] && continue
    expr="${line%|*}"
    expected="${line##*|}"
    # хвостовые пробелы выражения не срезаем: калькулятор их и так пропускает,
    # а строка из одних пробелов нужна для теста "пустое выражение"
    expected="$(echo "$expected" | sed 's/^ *//; s/ *$//')"

    output="$(printf '%s\n' "$expr" | ./lab1)"
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

echo "Пройдено: $pass, провалено: $fail"
(( fail == 0 ))
