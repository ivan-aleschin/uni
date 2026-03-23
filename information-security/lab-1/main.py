import os
import string


class SubstitutionCipher:
    """
    Класс для шифрования и дешифрования текста методом моноалфавитной подстановки.
    Использует английский алфавит согласно Варианту 1.
    """

    def __init__(self, key: str):
        self.alphabet = string.ascii_uppercase
        self.key = key.upper()

        if len(self.alphabet) != len(self.key) or set(self.alphabet) != set(self.key):
            raise ValueError(
                "Ключ должен содержать все 26 букв английского алфавита без повторений."
            )

        # Создаем таблицы перевода для верхнего и нижнего регистра
        self.encode_map = str.maketrans(
            self.alphabet + self.alphabet.lower(), self.key + self.key.lower()
        )
        self.decode_map = str.maketrans(
            self.key + self.key.lower(), self.alphabet + self.alphabet.lower()
        )

    def encrypt(self, text: str) -> str:
        """Шифрует исходный текст."""
        return text.translate(self.encode_map)

    def decrypt(self, text: str) -> str:
        """Дешифрует криптограмму обратно в исходный текст."""
        return text.translate(self.decode_map)


def main():
    # Ключ - перестановка английского алфавита
    key = "QWERTYUIOPASDFGHJKLZXCVBNM"
    cipher = SubstitutionCipher(key)

    input_filename = "input.txt"
    output_encrypted = "encrypted.txt"
    output_decrypted = "decrypted.txt"

    # Если файла нет, создадим его с тестовыми данными
    if not os.path.exists(input_filename):
        with open(input_filename, "w", encoding="utf-8") as f:
            f.write(
                "Information Security is crucial. This is Lab 1 for Substitution Cipher!"
            )

    # 1. Чтение исходных данных
    with open(input_filename, "r", encoding="utf-8") as f:
        original_text = f.read()

    print("=== ИСХОДНЫЙ ТЕКСТ ===")
    print(original_text)
    print("======================\n")

    # 2. Шифрование
    encrypted_text = cipher.encrypt(original_text)
    with open(output_encrypted, "w", encoding="utf-8") as f:
        f.write(encrypted_text)

    print("=== ЗАШИФРОВАННЫЙ ТЕКСТ (КРИПТОГРАММА) ===")
    print(encrypted_text)
    print("==========================================\n")

    # 3. Дешифрование
    with open(output_encrypted, "r", encoding="utf-8") as f:
        text_to_decrypt = f.read()

    decrypted_text = cipher.decrypt(text_to_decrypt)
    with open(output_decrypted, "w", encoding="utf-8") as f:
        f.write(decrypted_text)

    print("=== РАСШИФРОВАННЫЙ ТЕКСТ ===")
    print(decrypted_text)
    print("============================\n")

    # Проверка на совпадение
    if original_text == decrypted_text:
        print("[УСПЕХ] Исходный текст и расшифрованный текст полностью совпадают.")
    else:
        print("[ОШИБКА] Дешифрование прошло некорректно.")


if __name__ == "__main__":
    main()
