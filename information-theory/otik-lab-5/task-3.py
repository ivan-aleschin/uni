import struct
from typing import List, Tuple, Optional


class LZ77Encoder:
    def __init__(self, prefix_char: int):
        self.prefix_char = prefix_char

    def encode(self, data: bytes) -> bytes:
        """Сжатие данных методом LZ77 с односимвольным префиксом"""
        result = bytearray()
        i = 0
        n = len(data)

        while i < n:
            current_char = data[i]

            # Проверяем, является ли текущий символ префиксным
            if current_char == self.prefix_char:
                # Ищем цепочку одинаковых префиксных символов
                length = 1
                while i + length < n and data[i + length] == self.prefix_char and length < 258:  # L_max = 257
                    length += 1

                if length > 2:
                    # Цепочка из L > 2 символов p...p как (p:8, (L-1):8, p:8)
                    result.extend([self.prefix_char, (length - 1) & 0xFF, self.prefix_char])
                    i += length
                else:
                    # Одиночный p как (p:8, 0:8)
                    result.extend([self.prefix_char, 0])
                    i += 1

            else:
                # Проверяем, есть ли цепочка из L > 4 одинаковых символов c...c, c != p
                length = 1
                while (i + length < n and
                       data[i + length] == current_char and
                       data[i + length] != self.prefix_char and
                       length < 258):  # L_max = 257
                    length += 1

                if length > 4:
                    # Цепочка из L > 4 одинаковых символов c...c, c != p как (p:8, (L-3):8, c:8)
                    result.extend([self.prefix_char, (length - 3) & 0xFF, current_char])
                    i += length
                else:
                    # Обычный символ c != p записывается как (c:8)
                    result.append(current_char)
                    i += 1

        return bytes(result)


class LZ77Decoder:
    def __init__(self, prefix_char: int):
        self.prefix_char = prefix_char

    def decode(self, compressed_data: bytes) -> bytes:
        """Разжатие сжатых данных"""
        result = bytearray()
        i = 0
        n = len(compressed_data)

        while i < n:
            current_char = compressed_data[i]

            if current_char == self.prefix_char and i + 1 < n:
                length_code = compressed_data[i + 1]

                if length_code == 0:
                    # Одиночный p: (p:8, 0:8)
                    result.append(self.prefix_char)
                    i += 2

                elif i + 2 < n:
                    next_char = compressed_data[i + 2]

                    if next_char == self.prefix_char:
                        # Цепочка префиксных символов: (p:8, (L-1):8, p:8)
                        length = length_code + 1
                        result.extend([self.prefix_char] * length)
                        i += 3
                    else:
                        # Цепочка одинаковых символов: (p:8, (L-3):8, c:8)
                        length = length_code + 3
                        result.extend([next_char] * length)
                        i += 3
                else:
                    # Некорректные данные, обрабатываем как обычный символ
                    result.append(current_char)
                    i += 1
            else:
                # Обычный символ
                result.append(current_char)
                i += 1

        return bytes(result)


def calculate_optimal_prefix(data: bytes) -> int:
    """Вычисляет оптимальный префиксный символ на основе частотности"""
    if not data:
        return 0

    # Считаем частоты символов
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1

    # Находим символ с максимальной частотой
    max_freq = max(freq)
    optimal_prefix = freq.index(max_freq)

    return optimal_prefix


def compress_file(input_file: str, output_file: str):
    """Сжатие файла"""
    with open(input_file, 'rb') as f:
        data = f.read()

    # Вычисляем оптимальный префикс
    prefix_char = calculate_optimal_prefix(data)

    # Кодируем данные
    encoder = LZ77Encoder(prefix_char)
    compressed_data = encoder.encode(data)

    # Сохраняем с префиксом в начале файла
    with open(output_file, 'wb') as f:
        # Записываем префиксный символ как первый байт
        f.write(bytes([prefix_char]))
        f.write(compressed_data)

    original_size = len(data)
    compressed_size = len(compressed_data) + 1  # +1 для байта префикса
    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

    print(f"Сжатие завершено:")
    print(f"Исходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}%")
    print(f"Оптимальный префикс: {prefix_char} ('{chr(prefix_char) if 32 <= prefix_char < 127 else '?'}')")


def decompress_file(input_file: str, output_file: str):
    """Разжатие файла"""
    with open(input_file, 'rb') as f:
        # Читаем префиксный символ из первого байта
        prefix_char = f.read(1)[0]
        compressed_data = f.read()

    # Декодируем данные
    decoder = LZ77Decoder(prefix_char)
    decompressed_data = decoder.decode(compressed_data)

    # Сохраняем разжатые данные
    with open(output_file, 'wb') as f:
        f.write(decompressed_data)

    print(f"Разжатие завершено:")
    print(f"Использованный префикс: {prefix_char}")
    print(f"Размер разжатых данных: {len(decompressed_data)} байт")


def calculate_min_max_values():
    """Вычисление минимальных и максимальных значений для варианта"""
    print("Анализ параметров сжатия:")
    print("Формат записи:")
    print("1. Одиночный символ p: (p:8, 0:8)")
    print("2. Цепочка L > 2 символов p...p: (p:8, (L-1):8, p:8)")
    print("3. Цепочка L > 4 одинаковых символов c...c, c != p: (p:8, (L-3):8, c:8)")
    print("4. Обычный символ c != p: (c:8)")

    print("\nДиапазоны значений:")
    print("S (смещение): не используется в данной модификации")
    print("L (длина):")
    print("  - Для цепочек p...p: L_min = 3, L_max = 257")
    print("  - Для цепочек c...c: L_min = 5, L_max = 257")
    print("  - Кодируется как (L-1) или (L-3) в 8 битах (0-255)")

    print("\nРазмеры записей:")
    print("  - Одиночный символ: 2 байта")
    print("  - Цепочка символов: 3 байта")
    print("  - Обычный символ: 1 байт")


def main():
    """Основная функция программы"""
    print("LZ77 Codec с односимвольным префиксом")
    print("=====================================")

    while True:
        print("\nВыберите действие:")
        print("1 - Сжать файл")
        print("2 - Разжать файл")
        print("3 - Показать параметры сжатия")
        print("4 - Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            input_file = input("Введите имя файла для сжатия: ")
            output_file = input("Введите имя выходного файла: ")
            try:
                compress_file(input_file, output_file)
            except Exception as e:
                print(f"Ошибка при сжатии: {e}")

        elif choice == '2':
            input_file = input("Введите имя файла для разжатия: ")
            output_file = input("Введите имя выходного файла: ")
            try:
                decompress_file(input_file, output_file)
            except Exception as e:
                print(f"Ошибка при разжатии: {e}")

        elif choice == '3':
            calculate_min_max_values()

        elif choice == '4':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


# Тестирование
def test_compression():
    """Функция для тестирования корректности работы кодера/декодера"""
    print("Тестирование работы кодера...")

    # Тестовые данные
    test_data = b"AAAAABBBBBCCCCC" + b"X" * 10 + b"YYYYY"

    # Вычисляем оптимальный префикс
    prefix = calculate_optimal_prefix(test_data)
    print(f"Оптимальный префикс для тестовых данных: {prefix}")

    # Тестируем кодирование/декодирование
    encoder = LZ77Encoder(prefix)
    decoder = LZ77Decoder(prefix)

    compressed = encoder.encode(test_data)
    decompressed = decoder.decode(compressed)

    print(f"Исходные данные: {test_data[:50]}...")
    print(f"Сжатые данные: {compressed[:50]}...")
    print(f"Разжатые данные: {decompressed[:50]}...")
    print(f"Корректность: {test_data == decompressed}")


if __name__ == "__main__":
    # Запуск тестирования
    test_compression()
    print("\n" + "=" * 50)

    # Запуск основной программы
    main()