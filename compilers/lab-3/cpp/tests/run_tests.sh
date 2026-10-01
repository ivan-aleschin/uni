#!/usr/bin/env bash
# Тесты ЛР3: для каждой цепочки сверяем заключение автомата с ожидаемым,
# для испорченных грамматик — что программа падает с нужным сообщением.
# Запуск: make test или bash tests/run_tests.sh (из папки cpp/).

cd "$(dirname "$0")/.." || exit 1
make -s lab3 || exit 1
passed=0
failed=0
BIN=(./lab3)  # команда запуска программы

# accept ФАЙЛ ЦЕПОЧКА... — все цепочки должны допускаться
# reject ФАЙЛ ЦЕПОЧКА... — ни одна не должна допускаться
check() {
    local want=$1 file=$2
    shift 2
    for s in "$@"; do
        local out
        out=$(printf '%s\n' "$s" | "${BIN[@]}" "$file" | grep '^Заключение')
        local got=unknown
        if [[ $out == *"НЕ ДОПУСКАЕТСЯ"* ]]; then got=reject
        elif [[ $out == *"ДОПУСКАЕТСЯ"* ]]; then got=accept
        fi
        if [[ $got == "$want" ]]; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
            echo "ОШИБКА: $file «$s»: ожидалось $want, получено $got"
        fi
    done
}
accept() { check accept "$@"; }
reject() { check reject "$@"; }

# bad ФАЙЛ ФРАГМЕНТ — грамматика с ошибкой: код возврата 1 и фрагмент в сообщении
bad() {
    local file=$1 fragment=$2 out code
    out=$("${BIN[@]}" "$file" </dev/null 2>&1)
    code=$?
    if [[ $code -eq 1 && $out == *"$fragment"* ]]; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
        echo "ОШИБКА: $file: ожидалась ошибка «$fragment», получено (код $code): $out"
    fi
}

# Весь набор проверок.
suite() {
    # Пример 1 преподавателя: E>mT|!T|T, T>/P/, P>R|S, R>C-C, C>a|b|c|0|>, S>C|CS
    accept examples/test1.txt '/a-b/' 'm/abc/' '!/>/' '/0-0/' '/>->/' 'm/a/' '/ab0c>/' '! / a - c /'
    reject examples/test1.txt '/a-/' '/a' '//' 'a-b' '/a-b' 'mm/a/' '/a-b-c/' '/A/' 'ε'

    # Пример 2: идентификатор — буква, потом буквы и цифры
    accept examples/test2.txt 'x' 'x1y2' 'ab12xy' 'y0' 'abxy' 'a0123456789'
    reject examples/test2.txt '1x' 'x-1' 'ab12cd' '9' 'z' 'ε'
    # Длинная цепочка (5000 символов): перебор без рекурсии, стек вызовов не переполняется
    accept examples/test2.txt "$(printf 'x%.0s' {1..5000})"

    # Пример 3 (левая рекурсия S>Sa|Sb): a, или ≥2 символов на конце a, или b и ≥1 символ
    accept examples/test3.txt 'a' 'ba' 'bb' 'abba' 'aa' 'bab' 'bbbbbbbbbbbbbbbbbbba' 'babababababababababb'
    reject examples/test3.txt 'b' 'ab' 'abb' 'c' 'ε' 'abababababababababababababababababababab'

    # Грамматика из методички: E>E+T|T, T>T*F|F, F>(E)|a — левая рекурсия
    accept tests/expr.txt 'a' 'a+a*a' 'a + a * ( a + a )' '((a))*a+a*a+a' '((((((((a))))))))+a*a*a*a*a*a+a' \
        'a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a' '(((a+a)*(a+a))*((a+a)*(a+a)))+a*(a+a*(a+a))'
    # Символы вне ASCII не входят в P: отказ сразу, без разбора по байтам UTF-8
    reject tests/expr.txt 'aé' 'Ж+a' '€'
    reject tests/expr.txt 'a+' '(a' 'aa' ')a(' '()' '+a' 'a**a' '((((((((((((((((a)))))))))))))))' \
        'a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+a+'

    # ε-правило: S>aSbS|ε — правильные скобочные последовательности из a и b
    accept tests/eps.txt 'ε' 'ab' 'aabbab' 'aaabbbab'
    reject tests/eps.txt 'a' 'ba' 'aab' 'abba'

    # Левая рекурсия через обнуляемый нетерминал: S>SA|a, A>ε (нужна граница высоты магазина)
    accept tests/eps_left.txt 'a'
    reject tests/eps_left.txt 'aa' 'b' 'ε'

    # Цепные циклы S>A, A>B, B>S (нужна проверка повторов)
    accept tests/cycle.txt 'x' 'y' 'xy' 'xyx' 'yyy'
    reject tests/cycle.txt 'z' 'ε' 'xz'

    # Пробел как терминал (~): слова из a через одиночный пробел
    accept tests/space.txt 'a' 'aa a' 'a~aa~a'
    reject tests/space.txt 'a  a' 'a ' ' a'

    # Непродуктивный нетерминал B (из него ничего не выводится)
    accept tests/nonproductive.txt 'a'
    reject tests/nonproductive.txt 'b' 'bb'

    # Ошибки в файле грамматики
    bad tests/bad/no_arrow.txt "строка 2: нет символа '>'"
    bad tests/bad/long_left.txt 'левая часть «ab»'
    bad tests/bad/lower_left.txt 'левая часть «e»'
    bad tests/bad/empty_left.txt 'левая часть «»'
    bad tests/bad/undefined.txt 'нетерминал T встречается в правой части'
    bad tests/bad/empty.txt 'нет ни одного правила'
    bad tests/bad/cyrillic.txt 'только печатные ASCII'
    bad tests/bad/missing.txt 'не удалось открыть файл'
}

suite

echo "Пройдено: $passed, не пройдено: $failed"
[[ $failed -eq 0 ]]
