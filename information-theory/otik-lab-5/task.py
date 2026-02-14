import argparse
import os
import sys


class RLEEncoder:
    """
    Наивное RLE сжатие (Вариант 2)
    Формат: (L, c) где L - длина цепочки (1 байт), c - символ
    L̃ = L (фактическая длина), Lmax = 255
    """

    def encode(self, data):
        """Кодирование данных методом RLE"""
        if not data:
            return b""

        result = []
        i = 0
        n = len(data)

        while i < n:
            current_char = data[i]
            count = 1

            # Подсчитываем количество подряд идущих одинаковых символов
            while i + count < n and data[i + count] == current_char and count < 255:
                count += 1

            # Записываем пару (длина, символ)
            result.append(bytes([count, current_char]))
            i += count

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование RLE данных"""
        if not encoded_data:
            return b""

        result = []
        i = 0
        n = len(encoded_data)

        while i < n:
            if i + 1 >= n:
                break

            count = encoded_data[i]
            char = encoded_data[i + 1]

            # Восстанавливаем исходную последовательность
            result.append(bytes([char]) * count)
            i += 2

        return b"".join(result)


class LZ78Encoder:
    """
    LZ78 сжатие (Вариант 2)
    Формат: (d, l, c) где:
    d - номер в словаре (12 бит), l - длина совпадения (4 бита), c - следующий символ (8 бит)
    """

    def encode(self, data):
        """Кодирование данных методом LZ78"""
        if not data:
            return b""

        dictionary = {b"": 0}
        next_code = 1
        result = []
        i = 0
        n = len(data)

        while i < n:
            current_match = b""
            best_match = b""
            best_code = 0

            # Ищем наибольшее совпадение в словаре
            j = i
            while j < n:
                current_match += bytes([data[j]])
                if current_match in dictionary:
                    best_match = current_match
                    best_code = dictionary[current_match]
                    j += 1
                else:
                    break

            if j < n:
                next_char = data[j]
            else:
                next_char = 0  # Специальный маркер конца

            # Формируем код: d (12 бит), l (4 бита), c (8 бит)
            d = best_code
            l = len(best_match)
            c = next_char

            # Упаковываем в 3 байта
            code_bytes = bytes([
                (d >> 4) & 0xFF,  # Старшие 8 бит d
                ((d & 0x0F) << 4) | (l & 0x0F),  # Младшие 4 бита d + 4 бита l
                c & 0xFF  # Символ c
            ])

            result.append(code_bytes)

            # Добавляем новую строку в словарь
            if best_match + bytes([next_char]) not in dictionary and next_code < 4096:
                dictionary[best_match + bytes([next_char])] = next_code
                next_code += 1

            i = j + 1 if j < n else j

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование LZ78 данных"""
        if not encoded_data:
            return b""

        dictionary = {0: b""}
        next_code = 1
        result = []
        i = 0
        n = len(encoded_data)

        while i + 2 < n:
            # Извлекаем упакованные данные
            byte1 = encoded_data[i]
            byte2 = encoded_data[i + 1]
            byte3 = encoded_data[i + 2]

            # Распаковываем d, l, c
            d = (byte1 << 4) | ((byte2 >> 4) & 0x0F)
            l = byte2 & 0x0F
            c = byte3

            # Получаем строку из словаря
            if d in dictionary:
                decoded_string = dictionary[d] + bytes([c])
            else:
                decoded_string = bytes([c])

            result.append(decoded_string)

            # Добавляем в словарь
            if next_code < 4096:
                dictionary[next_code] = decoded_string
                next_code += 1

            i += 3

        return b"".join(result)


class LZ77Encoder:
    """
    LZ77 сжатие (Вариант 1)
    Формат: (d, l, c) где:
    d - смещение (12 бит), l - длина совпадения (4 бита), c - следующий символ (8 бит)
    """

    def encode(self, data, window_size=4095, lookahead_size=15):
        """Кодирование данных методом LZ77"""
        if not data:
            return b""

        result = []
        i = 0
        n = len(data)

        while i < n:
            # Определяем границы окна
            search_start = max(0, i - window_size)
            search_buffer = data[search_start:i]
            lookahead_buffer = data[i:min(i + lookahead_size, n)]

            best_match_length = 0
            best_match_distance = 0
            next_char = lookahead_buffer[0] if lookahead_buffer else 0

            # Ищем наибольшее совпадение в search_buffer
            for length in range(1, len(lookahead_buffer) + 1):
                pattern = lookahead_buffer[:length]

                # Ищем паттерн в search_buffer
                pos = search_buffer.rfind(pattern)
                if pos != -1:
                    distance = len(search_buffer) - pos
                    if length > best_match_length:
                        best_match_length = length
                        best_match_distance = distance
                        if i + length < n:
                            next_char = data[i + length]
                        else:
                            next_char = 0

            # Формируем код
            d = min(best_match_distance, 4095)
            l = min(best_match_length, 15)
            c = next_char

            # Упаковываем в 3 байта
            code_bytes = bytes([
                (d >> 4) & 0xFF,  # Старшие 8 бит d
                ((d & 0x0F) << 4) | (l & 0x0F),  # Младшие 4 бита d + 4 бита l
                c & 0xFF  # Символ c
            ])

            result.append(code_bytes)
            i += best_match_length + 1 if best_match_length > 0 else 1

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование LZ77 данных"""
        if not encoded_data:
            return b""

        result = []
        i = 0
        n = len(encoded_data)

        while i + 2 < n:
            # Извлекаем упакованные данные
            byte1 = encoded_data[i]
            byte2 = encoded_data[i + 1]
            byte3 = encoded_data[i + 2]

            # Распаковываем d, l, c
            d = (byte1 << 4) | ((byte2 >> 4) & 0x0F)
            l = byte2 & 0x0F
            c = byte3

            if d == 0 and l == 0:
                # Случай без совпадения
                result.append(bytes([c]))
            else:
                # Копируем из уже декодированных данных
                start_pos = len(result) - d
                for j in range(l):
                    if start_pos + j < len(result):
                        result.append(bytes([result[start_pos + j][0]]))
                result.append(bytes([c]))

            i += 3

        return b"".join(result)


def main():
    parser = argparse.ArgumentParser(description='Лабораторная работа 5: Сжатие данных')
    parser.add_argument('method', choices=['rle', 'lz78', 'lz77'], help='Метод сжатия')
    parser.add_argument('action', choices=['encode', 'decode'], help='Действие: кодирование или декодирование')
    parser.add_argument('input_file', help='Входной файл')
    parser.add_argument('output_file', help='Выходной файл')

    args = parser.parse_args()

    # Читаем входной файл
    try:
        with open(args.input_file, 'rb') as f:
            input_data = f.read()
    except Exception as e:
        print(f"Ошибка чтения файла {args.input_file}: {e}")
        return 1

    # Выбираем кодер/декодер
    if args.method == 'rle':
        coder = RLEEncoder()
    elif args.method == 'lz78':
        coder = LZ78Encoder()
    elif args.method == 'lz77':
        coder = LZ77Encoder()
    else:
        print(f"Неизвестный метод: {args.method}")
        return 1

    # Выполняем действие
    try:
        if args.action == 'encode':
            output_data = coder.encode(input_data)
            # Вычисляем степень сжатия
            original_size = len(input_data)
            compressed_size = len(output_data)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            print(f"Исходный размер: {original_size} байт")
            print(f"Сжатый размер: {compressed_size} байт")
            print(f"Степень сжатия: {compression_ratio:.2f}%")
        else:
            output_data = coder.decode(input_data)

        # Записываем результат
        with open(args.output_file, 'wb') as f:
            f.write(output_data)

        print(f"Успешно выполнено {args.action} для метода {args.method}")

    except Exception as e:
        print(f"Ошибка при выполнении {args.action}: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Демонстрация работы кодеков
    print("Демонстрация работы кодеков:")
    print("=" * 50)

    # Тестовые данные
    test_data = b"AAAABBBCCDAA" * 10  # Простые повторения
    test_data2 = b"ABABABAABABABAB" * 5  # Более сложный паттерн

    # RLE
    print("RLE кодирование:")
    rle = RLEEncoder()
    encoded = rle.encode(test_data)
    decoded = rle.decode(encoded)
    print(f"Исходные: {len(test_data)} байт")
    print(f"Сжатые: {len(encoded)} байт")
    print(f"Совпадение: {test_data == decoded}")
    print()

    # LZ78
    print("LZ78 кодирование:")
    lz78 = LZ78Encoder()
    encoded = lz78.encode(test_data2)
    decoded = lz78.decode(encoded)
    print(f"Исходные: {len(test_data2)} байт")
    print(f"Сжатые: {len(encoded)} байт")
    print(f"Совпадение: {test_data2 == decoded}")
    print()

    # LZ77
    print("LZ77 кодирование:")
    lz77 = LZ77Encoder()
    encoded = lz77.encode(test_data2)
    decoded = lz77.decode(encoded)
    print(f"Исходные: {len(test_data2)} байт")
    print(f"Сжатые: {len(encoded)} байт")
    print(f"Совпадение: {test_data2 == decoded}")
    print()

    # Если переданы аргументы командной строки
    if len(sys.argv) > 1:
        sys.exit(main())