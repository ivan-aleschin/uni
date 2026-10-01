"""Тесты ЛР5: прогоняет все примеры из examples/ и сверяет вывод с эталоном.

Для examples/<имя>.cbas эталон лежит в <имя>.expected (stdout и stderr вместе),
ввод для scan — в <имя>.in. Программы err_* должны завершаться с кодом 1, остальные — с 0.
Запуск: python3 tests.py  (или python3 tests.py -v)
"""

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from interpreter import Interpreter
from lexer import CbasError, Tok, tokenize
import main

HERE = Path(__file__).parent
EXAMPLES = HERE / "examples"


def run_example(program: Path) -> tuple[str, int]:
    """Запускает интерпретатор как отдельный процесс, как это делает пользователь."""
    stdin = program.with_suffix(".in")
    result = subprocess.run(
        [sys.executable, "-u", str(HERE / "main.py"), str(program)],
        input=stdin.read_text(encoding="utf-8") if stdin.exists() else "",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
    )
    return result.stdout, result.returncode


class ExamplesTest(unittest.TestCase):
    def test_examples(self) -> None:
        programs = sorted(EXAMPLES.glob("*.cbas"))
        self.assertTrue(programs, "в examples/ нет программ")
        for program in programs:
            with self.subTest(program=program.name):
                output, code = run_example(program)
                expected = program.with_suffix(".expected").read_text(encoding="utf-8")
                self.assertEqual(output, expected)
                self.assertEqual(code, 1 if program.name.startswith("err_") else 0)


class LexerTest(unittest.TestCase):
    def test_internal_format(self) -> None:
        tokens = tokenize('for i = 1 to 10 { print "x", i; }')
        codes = [int(t.code) for t in tokens]
        self.assertEqual(codes, [3, 10, 28, 11, 4, 11, 26, 1, 12, 33, 10, 34, 27, 0])

    def test_relops_two_chars(self) -> None:
        codes = [t.code for t in tokenize("a == b != c = d < e > f")]
        self.assertEqual(codes[1:-1:2], [Tok.EQ, Tok.NE, Tok.ASSIGN, Tok.LT, Tok.GT])

    def test_line_numbers(self) -> None:
        with self.assertRaises(CbasError) as err:
            tokenize("a = 1\n\nb = 2 # 3")
        self.assertEqual(err.exception.line, 3)


def run_source(source: str, stdin: str = "") -> str:
    """Выполняет программу из строки и возвращает то, что она напечатала."""
    out = io.StringIO()
    Interpreter(tokenize(source), io.StringIO(stdin), out, io.StringIO()).run()
    return out.getvalue()


class InterpreterTest(unittest.TestCase):
    def test_skipped_branch_is_not_computed(self) -> None:
        # невыполняемая ветка только разбирается: переполнения в ней быть не должно
        self.assertEqual(run_source('if 0 > 1 { x = 100000 * 100000 } print "ok";'), "ok\n")

    def test_int_min_div_minus_one(self) -> None:
        with self.assertRaises(CbasError) as err:
            run_source("scan m; print m / (0 - 1);", "-2147483648\n")
        self.assertTrue(err.exception.runtime)

    def test_deep_nesting_is_error_not_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / "deep.cbas"
            program.write_text("x = " + "(" * 1000 + "1" + ")" * 1000, encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main.main(["main.py", str(program)])
        self.assertEqual(code, 1)
        self.assertIn("слишком глубокая вложенность", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
