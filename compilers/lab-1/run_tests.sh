#!/usr/bin/env bash
# Прогоняет каждую строку tests.txt через калькулятор и сверяет вывод с ожиданием.
#
#   ./run_tests.sh              обе версии + побайтное сравнение их вывода
#   ./run_tests.sh cpp          только C++ (cpp/lab1, собирается при необходимости)
#   ./run_tests.sh python       только Python (python3 python/main.py)
#   ./run_tests.sh <команда…>   любая команда, читающая выражения со stdin
cd "$(dirname "$0")"

CPP=(./cpp/lab1)
PY=(python3 python/main.py)

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

build_cpp() {
    make -s -C cpp >/dev/null || { echo "не удалось собрать cpp/lab1"; exit 1; }
}

case "${1:-all}" in
    cpp)
        build_cpp
        run_suite "C++" "${CPP[@]}"
        ;;
    python)
        run_suite "Python" "${PY[@]}"
        ;;
    all)
        build_cpp
        status=0
        run_suite "C++" "${CPP[@]}" || status=1
        echo
        run_suite "Python" "${PY[@]}" || status=1
        echo
        # Обе версии должны печатать одно и то же байт в байт, в том числе таблицу --trace.
        exprs="$(grep -v -e '^#' -e '^ *$' tests.txt | sed 's/|[^|]*$//')"
        for flag in "" --trace; do
            if cmp -s <(printf '%s\n' "$exprs" | "${CPP[@]}" $flag) \
                      <(printf '%s\n' "$exprs" | "${PY[@]}" $flag); then
                echo "Вывод C++ и Python совпадает побайтно ${flag:-(без флагов)}"
            else
                echo "Вывод C++ и Python РАЗЛИЧАЕТСЯ ${flag:-(без флагов)}"
                status=1
            fi
        done
        exit $status
        ;;
    *)
        run_suite "$1" "$@"
        ;;
esac
