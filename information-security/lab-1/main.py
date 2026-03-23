"""
Лабораторная работа №1 — Шифрование методом подстановки
Вариант 1: Таблица 1.2, Столбец 3
Исходный алфавит: английский (A-Z + спецсимволы)
"""

import os
from typing import Final


class SubstitutionCipher:
    """
    Моноалфавитный шифр подстановки.
    """

    SUBSTITUTION_TABLE: Final[dict[str, str]] = {
        "A": "Z",
        "B": " ",
        "C": ".",
        "D": "X",
        "E": "Y",
        "F": ",",
        "G": "!",
        "H": "S",
        "I": "T",
        "J": ":",
        "K": ";",
        "L": "Q",
        "M": "R",
        "N": "?",
        "O": "-",
        "P": "N",
        "Q": "O",
        "R": "P",
        "S": "L",
        "T": "M",
        "U": "U",  # Изменено на уникальное 'U' (была коллизия: 'P' тоже давал 'N')
        "V": "V",  # Изменено на уникальное 'V' (была коллизия: 'Q' тоже давал 'O')
        "W": "W",  # Изменено на уникальное 'W' (была коллизия: 'R' тоже давал 'P')
        "X": "A",
        "Y": "B",
        "Z": "C",
        " ": "D",
        ".": "E",
        ",": "F",
        "!": "G",
        ":": "H",
        ";": "I",
        "?": "J",
        "-": "K",
    }

    def __init__(self) -> None:
        self._encode: dict[str, str] = self.SUBSTITUTION_TABLE
        # Так как теперь все значения уникальны, обратная таблица строится однозначно
        self._decode: dict[str, str] = {v: k for k, v in self._encode.items()}

    def encrypt(self, text: str) -> str:
        """
        Шифрует исходный текст.
        Символы вне алфавита пропускаются без изменений.
        """
        return "".join(self._encode.get(ch, ch) for ch in text.upper())

    def decrypt(self, text: str) -> str:
        """
        Дешифрует криптограмму.
        Символы вне алфавита пропускаются без изменений.
        """
        return "".join(self._decode.get(ch, ch) for ch in text)

    def print_table(self) -> None:
        """Печатает таблицу шифрования для отчёта."""
        print("  Таблица подстановки (биекция):")
        items = list(self._encode.items())
        mid = len(items) // 2
        for (src1, enc1), (src2, enc2) in zip(items[:mid], items[mid:]):
            s1 = repr(src1) if src1 in " ." else src1
            e1 = repr(enc1) if enc1 in " ." else enc1
            s2 = repr(src2) if src2 in " ." else src2
            e2 = repr(enc2) if enc2 in " ." else enc2
            print(f"    {s1:>4} -> {e1:<4}  |  {s2:>4} -> {e2:<4}")


def _banner(title: str, width: int = 60) -> str:
    line = "=" * width
    return f"\n{line}\n  {title}\n{line}"


def main() -> None:
    cipher = SubstitutionCipher()

    input_file = "input.txt"
    encrypted_file = "encrypted.txt"
    decrypted_file = "decrypted.txt"

    # Создаём входной файл с примером на английском, если он отсутствует
    if not os.path.exists(input_file):
        sample = "INFORMATION SECURITY IS AN IMPORTANT TASK.\nTHIS IS LAB 1!"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"[INFO] Создан файл '{input_file}' с тестовым текстом.")

    with open(input_file, "r", encoding="utf-8") as f:
        original = f.read()

    print(_banner("ТАБЛИЦА ПОДСТАНОВКИ"))
    cipher.print_table()

    print(_banner("ИСХОДНЫЙ ТЕКСТ"))
    print(original)

    # 1. Шифрование
    encrypted = cipher.encrypt(original)
    with open(encrypted_file, "w", encoding="utf-8") as f:
        f.write(encrypted)

    print(_banner("ЗАШИФРОВАННЫЙ ТЕКСТ (КРИПТОГРАММА)"))
    print(encrypted)

    # 2. Дешифрование
    with open(encrypted_file, "r", encoding="utf-8") as f:
        cipher_from_file = f.read()

    decrypted = cipher.decrypt(cipher_from_file)
    with open(decrypted_file, "w", encoding="utf-8") as f:
        f.write(decrypted)

    print(_banner("РАСШИФРОВАННЫЙ ТЕКСТ"))
    print(decrypted)

    # 3. Верификация корректности
    print(_banner("ВЕРИФИКАЦИЯ"))
    reference = original.upper()

    if reference == decrypted:
        print("[УСПЕХ] Текст успешно и однозначно дешифрован.")
    else:
        print("[ОШИБКА] Возникли проблемы при расшифровке!")
        for i, (a, b) in enumerate(zip(reference, decrypted)):
            if a != b:
                print(f"  Позиция {i}: ожидалось {repr(a)}, получено {repr(b)}")
                break


if __name__ == "__main__":
    main()
