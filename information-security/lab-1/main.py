"""
Лабораторная работа №1 — Шифрование методом подстановки
Вариант 1: Таблица 1.2, Столбец 3
Исходный алфавит: русский (А–Я + пробел, 34 символа)
Подстановочный алфавит: латинские буквы + спецсимволы
"""

import os
from typing import Final


class SubstitutionCipher:
    """
    Моноалфавитный шифр подстановки.
    Таблица 1.2, Вариант 1, Столбец 3:
      - 34 символа исходного алфавита (А–Я + пробел)
      - Подстановочный алфавит: латиница + спецсимволы (!  : ; - . , ? V …)
    """

    # Таблица подстановки: русская буква (верхний регистр) → символ шифротекста
    # Источник: Таблица 1.2, строки 1–34, Столбец 3
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
        "U": "N",
        "V": "O",
        "W": "P",
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
        # Обратная таблица строится автоматически (биекция гарантирована таблицей)
        self._decode: dict[str, str] = {v: k for k, v in self._encode.items()}

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def encrypt(self, text: str) -> str:
        """
        Шифрует исходный русскоязычный текст.
        Символы вне алфавита (цифры, знаки препинания) пропускаются без изменений.
        """
        return "".join(self._encode.get(ch, ch) for ch in text.upper())

    def decrypt(self, text: str) -> str:
        """
        Дешифрует криптограмму обратно в исходный текст (верхний регистр).
        Символы вне подстановочного алфавита пропускаются без изменений.
        """
        return "".join(self._decode.get(ch, ch) for ch in text)

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    def print_table(self) -> None:
        """Печатает полную таблицу подстановки (для отчёта)."""
        header = (
            f"{'Исходный':>10}  →  {'Шифр':<6}  |  {'Исходный':>10}  →  {'Шифр':<6}"
        )
        print(header)
        print("-" * len(header))
        items = list(self._encode.items())
        mid = len(items) // 2
        for (src1, enc1), (src2, enc2) in zip(items[:mid], items[mid:]):
            src1_repr = repr(src1) if src1 == " " else src1
            src2_repr = repr(src2) if src2 == " " else src2
            enc1_repr = repr(enc1) if enc1 == " " else enc1
            enc2_repr = repr(enc2) if enc2 == " " else enc2
            print(
                f"{src1_repr:>10}  →  {enc1_repr:<6}  |  {src2_repr:>10}  →  {enc2_repr:<6}"
            )


# ----------------------------------------------------------------------
# Точка входа
# ----------------------------------------------------------------------


def _banner(title: str, width: int = 56) -> str:
    line = "=" * width
    return f"\n{line}\n  {title}\n{line}"


def main() -> None:
    cipher = SubstitutionCipher()

    input_file = "input.txt"
    encrypted_file = "encrypted.txt"
    decrypted_file = "decrypted.txt"

    # Создаём входной файл с примером, если он отсутствует
    if not os.path.exists(input_file):
        sample = (
            "ЗАЩИТА ИНФОРМАЦИИ ЯВЛЯЕТСЯ ВАЖНОЙ ЗАДАЧЕЙ\n"
            "ШИФРОВАНИЕ ОБЕСПЕЧИВАЕТ КОНФИДЕНЦИАЛЬНОСТЬ"
        )
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"[INFO] Создан файл '{input_file}' с тестовым текстом.")

    # 1. Читаем исходный текст
    with open(input_file, "r", encoding="utf-8") as f:
        original = f.read()

    print(_banner("ТАБЛИЦА ПОДСТАНОВКИ (Таблица 1.2, Столбец 3)"))
    cipher.print_table()

    print(_banner("ИСХОДНЫЙ ТЕКСТ"))
    print(original)

    # 2. Шифрование
    encrypted = cipher.encrypt(original)
    with open(encrypted_file, "w", encoding="utf-8") as f:
        f.write(encrypted)

    print(_banner("ЗАШИФРОВАННЫЙ ТЕКСТ (КРИПТОГРАММА)"))
    print(encrypted)

    # 3. Дешифрование (читаем из файла — имитируем передачу шифротекста)
    with open(encrypted_file, "r", encoding="utf-8") as f:
        cipher_from_file = f.read()

    decrypted = cipher.decrypt(cipher_from_file)
    with open(decrypted_file, "w", encoding="utf-8") as f:
        f.write(decrypted)

    print(_banner("РАСШИФРОВАННЫЙ ТЕКСТ"))
    print(decrypted)

    # 4. Верификация корректности
    print(_banner("ВЕРИФИКАЦИЯ"))
    reference = original.upper()
    if reference == decrypted:
        print("[УСПЕХ] Расшифрованный текст совпадает с исходным (верхний регистр).")
    else:
        print("[ОШИБКА] Обнаружено несоответствие:")
        for i, (a, b) in enumerate(zip(reference, decrypted)):
            if a != b:
                print(f"  Позиция {i}: ожидалось {repr(a)}, получено {repr(b)}")
                break


if __name__ == "__main__":
    main()
