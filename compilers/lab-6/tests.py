#!/usr/bin/env python3
"""Прогон примеров: для каждого examples/*.emark запускает процессор без цвета
и с рамкой и сверяет вывод с эталоном examples/*.expected.

В эталоне сначала идёт stdout (экраны), затем stderr (ошибки/предупреждения)
и в конце код возврата.  python3 tests.py --update перезаписывает эталоны
(после этого их надо просмотреть глазами).
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def run(doc):
    p = subprocess.run([sys.executable, "main.py", "--no-color", "--frame", f"examples/{doc.name}"],
                       cwd=HERE, capture_output=True, text=True)
    return p.stdout + p.stderr + f"код возврата: {p.returncode}\n"


def main():
    update = "--update" in sys.argv
    failed = 0
    docs = sorted((HERE / "examples").glob("*.emark"))
    for doc in docs:
        actual = run(doc)
        expected_file = doc.with_suffix(".expected")
        if update:
            expected_file.write_text(actual, encoding="utf-8")
            print(f"обновлён  {expected_file.name}")
            continue
        expected = expected_file.read_text(encoding="utf-8") if expected_file.exists() else None
        if actual == expected:
            print(f"OK    {doc.name}")
        else:
            failed += 1
            print(f"FAIL  {doc.name}" + ("" if expected is not None else " (нет эталона)"))
    if not update:
        print(f"\nпройдено {len(docs) - failed} из {len(docs)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
