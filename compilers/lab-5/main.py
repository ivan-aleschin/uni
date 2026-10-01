"""ЛР5 ТАЯК: интерпретатор языка CBAS.

Запуск: python3 main.py программа.cbas
"""

import sys

from interpreter import Interpreter
from lexer import CbasError, tokenize


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Использование: python3 main.py <программа.cbas>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"Не удалось открыть файл {argv[1]}: {e.strerror}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print(f"Файл {argv[1]} не в кодировке UTF-8", file=sys.stderr)
        return 2

    try:
        tokens = tokenize(source)  # внешний формат -> внутренний
        Interpreter(tokens).run()  # проверка синтаксиса, затем выполнение
    except CbasError as e:
        sys.stdout.flush()  # сначала всё, что программа успела напечатать
        print(e, file=sys.stderr)
        return 1
    except RecursionError:  # вложенность глубже стека вызовов Python (аналог FOR_COUNT из методички)
        sys.stdout.flush()
        print("Ошибка: слишком глубокая вложенность скобок или блоков", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
