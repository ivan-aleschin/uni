"""
Лабораторная работа №2 — Шифрование данных при помощи генератора псевдослучайных чисел
Вариант 1: Линейные конгруэнтные датчики ПСЧ, b = 6
"""

import os


class LinearCongruentialGenerator:
    """
    Линейный конгруэнтный датчик ПСЧ.
    T(i+1) = (A * T(i) + C) mod M
    """

    def __init__(self, a: int, c: int, m: int, seed: int) -> None:
        self.a = a
        self.c = c
        self.m = m
        self.state = seed

    def next(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def reset(self, seed: int) -> None:
        self.state = seed


class GammaCipher:
    """
    Шифрование гаммированием с использованием ЛКГ ПСЧ.
    """

    def __init__(self, a: int, c: int, b: int, seed: int) -> None:
        self.a = a
        self.c = c
        self.b = b
        self.m = 2**b
        self.seed = seed
        self.prng = LinearCongruentialGenerator(self.a, self.c, self.m, self.seed)

    def encrypt(self, text: str) -> list[int]:
        """Шифрует исходный текст."""
        self.prng.reset(self.seed)
        encrypted = []
        for char in text:
            gamma = self.prng.next()
            # Наложение гаммы (сложение по модулю 2)
            encrypted.append(ord(char) ^ gamma)
        return encrypted

    def decrypt(self, encrypted_data: list[int]) -> str:
        """Дешифрует криптограмму."""
        self.prng.reset(self.seed)
        decrypted_chars = []
        for enc_char in encrypted_data:
            gamma = self.prng.next()
            decrypted_chars.append(chr(enc_char ^ gamma))
        return "".join(decrypted_chars)

    def print_params(self) -> None:
        """Печатает параметры генератора для отчёта."""
        print("  Параметры линейного конгруэнтного датчика ПСЧ:")
        print(f"    Множитель (A): {self.a}")
        print(f"    Приращение (C): {self.c}")
        print(f"    Количество разрядов (b): {self.b}")
        print(f"    Модуль (M): {self.m}")
        print(f"    Начальное значение T(0): {self.seed}")


def _banner(title: str, width: int = 60) -> str:
    line = "=" * width
    return f"\n{line}\n  {title}\n{line}"


def main() -> None:
    # Вариант 1: Линейные конгруэнтные датчики ПСЧ, b = 6
    # Максимальный период M = 2^6 = 64
    # Условия: C нечетное, A mod 4 = 1
    a = 17
    c = 11
    b = 6
    seed = 7

    cipher = GammaCipher(a, c, b, seed)

    input_file = "input.txt"
    encrypted_file = "encrypted.txt"
    decrypted_file = "decrypted.txt"

    # Создаём входной файл с примером, если он отсутствует
    if not os.path.exists(input_file):
        sample = "Секретное сообщение для лабораторной работы №2!\nВариант 1."
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(sample)
        print(f"[INFO] Создан файл '{input_file}' с тестовым текстом.")

    with open(input_file, "r", encoding="utf-8") as f:
        original = f.read()

    print(_banner("ПАРАМЕТРЫ ГЕНЕРАТОРА ПСЧ"))
    cipher.print_params()

    print(_banner("ИСХОДНЫЙ ТЕКСТ"))
    print(original)

    # 1. Шифрование
    encrypted_data = cipher.encrypt(original)
    encrypted_str = " ".join(map(str, encrypted_data))

    with open(encrypted_file, "w", encoding="utf-8") as f:
        f.write(encrypted_str)

    print(_banner("ЗАШИФРОВАННЫЙ ТЕКСТ (КРИПТОГРАММА)"))
    print(encrypted_str)

    # 2. Дешифрование
    with open(encrypted_file, "r", encoding="utf-8") as f:
        cipher_from_file_str = f.read().strip()
        cipher_from_file = list(map(int, cipher_from_file_str.split()))

    decrypted = cipher.decrypt(cipher_from_file)
    with open(decrypted_file, "w", encoding="utf-8") as f:
        f.write(decrypted)

    print(_banner("РАСШИФРОВАННЫЙ ТЕКСТ"))
    print(decrypted)

    # 3. Верификация корректности
    print(_banner("ВЕРИФИКАЦИЯ"))
    if original == decrypted:
        print("[УСПЕХ] Текст успешно и однозначно дешифрован.")
    else:
        print("[ОШИБКА] Возникли проблемы при расшифровке!")

    # 4. Изменение параметра (задание 4)
    print(_banner("ИЗМЕНЕНИЕ ПАРАМЕТРА T(0) = 12"))
    changed_seed = 12
    cipher_new = GammaCipher(a, c, b, changed_seed)

    encrypted_data_new = cipher_new.encrypt(original)
    encrypted_str_new = " ".join(map(str, encrypted_data_new))

    print("  Шифрограмма с изменённым начальным значением:")
    print("  " + encrypted_str_new[:80] + "...")

    if encrypted_str != encrypted_str_new:
        print("\n[УСПЕХ] Шифрограммы отличаются при изменении параметра генератора.")
    else:
        print("\n[ОШИБКА] Шифрограммы совпадают!")

    wrong_decrypted = cipher_new.decrypt(encrypted_data)
    print("\n  Попытка расшифровать оригинальную криптограмму новым ключом:")
    print("  " + repr(wrong_decrypted[:40]) + "...")

    # 5. Демонстрация уязвимости малого b (M=64)
    print(_banner("ДЕМОНСТРАЦИЯ УЯЗВИМОСТИ МАЛОГО b (b=6, M=64)"))
    print("  Так как b=6, генератор выдает максимум 6 бит (число до 63).")
    print("  А русские буквы в Unicode занимают 11-12 бит (числа > 1000).")

    cipher_demo = GammaCipher(a, c, b + 0, seed)
    cipher_demo.prng.reset(seed)

    for char in original[:3]:
        gamma = cipher_demo.prng.next()
        char_code = ord(char)
        encrypted_code = char_code ^ gamma

        print(f"\n  Символ '{char}' (код {char_code}):")
        print(f"    Открытый текст: {char_code:012b}")
        print(f"    Гамма (6 бит):  {gamma:012b} (число {gamma})")
        print(f"    Шифротекст:     {encrypted_code:012b}")
        print("    -> Старшие биты остались без изменений")


if __name__ == "__main__":
    main()
