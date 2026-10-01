#!/usr/bin/env bash
# Автотесты ЛР2. Запуск: make test (или bash tests/run_tests.sh из папки cpp/).
# 1) строки из tests/cases.tsv: допускается / не допускается;
# 2) детерминизация var3_nd.txt совпадает с ручным построением;
# 3) ДКА, сохранённый в файл, читается обратно, детерминирован и даёт те же ответы;
# 4) синтаксические ошибки и висячие вершины находятся;
# 5) --dot пишет файлы графов;
# 6) файл с BOM и буквой в cp1251 читается без ошибок.
set -u
cd "$(dirname "$0")/.."
ROOT=$PWD
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
total_fail=0

make -s lab2 || exit 1

# Прогон всех проверок для одной версии: suite <название> <команда запуска ...>
suite() {
    local name=$1
    shift
    local BIN=("$@")
    local pass=0 fail=0 out n s f a b file str want verdict
    ok()  { pass=$((pass + 1)); }
    bad() { fail=$((fail + 1)); echo "ПРОВАЛ ($name): $*"; }

    # --- 1. строки ---
    while IFS=$'\t' read -r file str want; do
        [[ -z "$file" || "$file" == \#* ]] && continue
        out=$("${BIN[@]}" "$file" "$str")
        if [[ "$want" == "+" ]]; then verdict="\"$str\" — ДОПУСКАЕТСЯ"; else verdict="\"$str\" — НЕ ДОПУСКАЕТСЯ"; fi
        if grep -qF -- "$verdict" <<<"$out" && ! grep -q "ВНИМАНИЕ" <<<"$out"; then ok; else bad "$file \"$str\" ожидалось $want"; fi
    done < tests/cases.tsv

    # --- 2. детерминизация var3_nd совпадает с ручной ---
    "${BIN[@]}" examples/var3_nd.txt --dfa-out "$TMP/var3.dfa" "" >/dev/null
    if diff -u tests/var3_nd.dfa.expected "$TMP/var3.dfa"; then ok; else bad "ДКА для var3_nd.txt отличается от ручного"; fi

    # --- 3. ДКА читается обратно и детерминирован, ответы те же ---
    for f in examples/var3_nd.txt tests/manual_nfa.txt tests/ends_ab.txt tests/unicode.txt; do
        "${BIN[@]}" "$f" --dfa-out "$TMP/round.txt" "" >/dev/null
        out=$("${BIN[@]}" "$TMP/round.txt" "")
        if grep -q "Автомат ДЕТЕРМИНИРОВАН" <<<"$out"; then ok; else bad "ДКА из $f после перечитывания недетерминирован"; fi
        while IFS=$'\t' read -r file str want; do
            [[ "$file" == "$f" ]] || continue
            a=$("${BIN[@]}" "$f" "$str" | grep -F "\"$str\" —")
            b=$("${BIN[@]}" "$TMP/round.txt" "$str" | grep -F "\"$str\" —")
            [[ "${a%%:*}" == "${b%%:*}" ]] && ok || bad "ДКА из $f отвечает иначе на \"$str\""
        done < tests/cases.tsv
    done

    # --- 4. ошибки и висячие вершины ---
    out=$("${BIN[@]}" tests/errors.txt "")
    n=$(grep -c '^  строка [0-9]*: "' <<<"$out")
    [[ "$n" == 11 ]] && ok || bad "errors.txt: найдено синтаксических ошибок $n, ожидалось 11"
    grep -q "строка 15: правило q1,b=f0 уже было выше" <<<"$out" && ok || bad "errors.txt: не найден повтор"

    out=$("${BIN[@]}" tests/hanging.txt "")
    grep -q "Недостижимые из q0 состояния: q3 " <<<"$out" && ok || bad "hanging.txt: не найдено недостижимое q3"
    for s in "q4 — из него нет" "q5 — переходы есть" "q6 — переходы есть"; do
        grep -qF "  $s" <<<"$out" && ok || bad "hanging.txt: нет строки '$s'"
    done
    out=$("${BIN[@]}" tests/no_final.txt "")
    grep -q "конечных состояний (f<N>) нет" <<<"$out" && ok || bad "no_final.txt: нет предупреждения"

    # --- 5. Graphviz ---
    rm -f "$TMP"/g.* "$TMP"/board*
    cp examples/var3_nd.txt "$TMP/g.txt"
    "${BIN[@]}" "$TMP/g.txt" --dot "" >/dev/null
    [[ -s "$TMP/g.dot" && -s "$TMP/g.dfa.dot" ]] && ok || bad "--dot не создал файлы"
    grep -q 'q6 \[label="q6\\n{q1, q3, q4}"' "$TMP/g.dfa.dot" && ok || bad "в g.dfa.dot нет составной вершины q6"
    # имя без расширения и с "./": графы рядом с файлом, а не в ".dot"
    cp examples/var3_nd.txt "$TMP/board"
    (cd "$TMP" && "${BIN[@]}" ./board --dot "" >/dev/null)
    [[ -s "$TMP/board.dot" && -s "$TMP/board.dfa.dot" ]] && ok || bad "--dot для ./board записал не те файлы"

    # --- 6. BOM и cp1251 из Блокнота Windows ---
    out=$("${BIN[@]}" tests/bom_cp1251.txt "")
    grep -q "с ошибками: 0" <<<"$out" && ok || bad "bom_cp1251.txt: BOM или байт cp1251 дали ошибку"

    echo "$name — пройдено: $pass, провалено: $fail"
    total_fail=$((total_fail + fail))
}

suite C++ "$ROOT/lab2"

[[ "$total_fail" == 0 ]]
