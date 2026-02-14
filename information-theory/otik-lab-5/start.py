import os
import struct
import random
from pathlib import Path
import time


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


def create_test_files():
    """Создание тестовых файлов для всех алгоритмов"""
    test_dir = Path("compression_tests")
    test_dir.mkdir(exist_ok=True)

    # t1_100xA.bin - 100 символов 'A' (хорошо для RLE)
    with open(test_dir / "t1_100xA.bin", "wb") as f:
        f.write(b"A" * 100)

    # t2_50x00_plus_single00.bin - 50 нулевых байтов + отдельный нулевой байт
    with open(test_dir / "t2_50x00_plus_single00.bin", "wb") as f:
        f.write(b"\x00" * 50)
        f.write(b"\x00")

    # t3_mixed.bin - смешанные данные
    with open(test_dir / "t3_mixed.bin", "wb") as f:
        data = b"A" * 10 + b"B" * 5 + b"C" * 20 + b"D" * 3 + b"E" * 15
        f.write(data)

    # t4_edges.bin - граничные случаи
    with open(test_dir / "t4_edges.bin", "wb") as f:
        f.write(b"X" * 300)
        f.write(b"Y" * 1)
        f.write(b"Z" * 2)

    # t5_random_4k.bin - случайные данные 4KB
    with open(test_dir / "t5_random_4k.bin", "wb") as f:
        data = bytearray()
        i = 0
        while i < 4096:
            length = random.randint(1, 50)
            char = random.randint(0, 255)
            data.extend([char] * length)
            i += length
        f.write(bytes(data[:4096]))

    # t6_small_no_runs.bin - маленький файл без повторений
    with open(test_dir / "t6_small_no_runs.bin", "wb") as f:
        f.write(bytes(range(32)))

    # t7_text.bin - текстовые данные (хорошо для LZ)
    text = b"Hello world! This is a test text for compression algorithms. " * 50
    with open(test_dir / "t7_text.bin", "wb") as f:
        f.write(text)

    # t8_repeating_pattern.bin - повторяющийся паттерн (хорошо для LZ)
    pattern = b"ABCDEFGH" * 100
    with open(test_dir / "t8_repeating_pattern.bin", "wb") as f:
        f.write(pattern)

    print("Тестовые файлы созданы в папке 'compression_tests'")


def run_compression_tests():
    """Запуск тестов для всех алгоритмов сжатия"""
    test_dir = Path("compression_tests")

    # Инициализация кодеков
    rle_encoder = RLEEncoder()
    lz78_encoder = LZ78Encoder()
    lz77_encoder = LZ77Encoder()

    algorithms = {
        'RLE': rle_encoder,
        'LZ78': lz78_encoder,
        'LZ77': lz77_encoder
    }

    results = {}

    print("Тестирование всех алгоритмов сжатия:")
    print("=" * 80)

    # Получаем список тестовых файлов
    test_files = sorted([f for f in test_dir.glob("*.bin")])

    for algorithm_name, encoder in algorithms.items():
        print(f"\n{algorithm_name} тестирование:")
        print("-" * 40)

        algorithm_results = []

        for test_file in test_files:
            # Читаем исходные данные
            with open(test_file, "rb") as f:
                original_data = f.read()

            # Измеряем время кодирования
            start_time = time.time()
            encoded_data = encoder.encode(original_data)
            encode_time = time.time() - start_time

            # Измеряем время декодирования
            start_time = time.time()
            decoded_data = encoder.decode(encoded_data)
            decode_time = time.time() - start_time

            # Проверяем корректность
            is_correct = original_data == decoded_data

            # Вычисляем статистику
            original_size = len(original_data)
            encoded_size = len(encoded_data)
            compression_ratio = (1 - encoded_size / original_size) * 100 if original_size > 0 else 0

            result = {
                'file': test_file.name,
                'original_size': original_size,
                'encoded_size': encoded_size,
                'compression_ratio': compression_ratio,
                'encode_time': encode_time,
                'decode_time': decode_time,
                'is_correct': is_correct
            }

            algorithm_results.append(result)

            print(f"  {test_file.name}: {original_size} -> {encoded_size} байт "
                  f"({compression_ratio:+.2f}%) {'✓' if is_correct else '✗'}")

        results[algorithm_name] = algorithm_results

    # Вывод сравнительной таблицы
    print("\n\nСРАВНИТЕЛЬНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ:")
    print("=" * 100)
    print(
        f"{'Файл':<25} {'Алгоритм':<8} {'Исходный':<10} {'Сжатый':<10} {'Сжатие %':<10} {'Время код.':<12} {'Время дек.':<12} {'Корр.'}")
    print("-" * 100)

    for test_file in test_files:
        for algorithm_name in algorithms.keys():
            result = next(r for r in results[algorithm_name] if r['file'] == test_file.name)
            print(f"{test_file.name:<25} {algorithm_name:<8} {result['original_size']:<10} "
                  f"{result['encoded_size']:<10} {result['compression_ratio']:>+8.2f}% "
                  f"{result['encode_time']:>11.4f}s {result['decode_time']:>11.4f}s "
                  f"{'✓' if result['is_correct'] else '✗':^6}")

    # Анализ эффективности по алгоритмам
    print("\n\nАНАЛИЗ ЭФФЕКТИВНОСТИ ПО АЛГОРИТМАМ:")
    print("=" * 80)

    for algorithm_name in algorithms.keys():
        algorithm_results = results[algorithm_name]
        avg_compression = sum(r['compression_ratio'] for r in algorithm_results) / len(algorithm_results)
        avg_encode_time = sum(r['encode_time'] for r in algorithm_results) / len(algorithm_results)
        avg_decode_time = sum(r['decode_time'] for r in algorithm_results) / len(algorithm_results)
        success_rate = sum(1 for r in algorithm_results if r['is_correct']) / len(algorithm_results) * 100

        print(f"{algorithm_name}:")
        print(f"  Среднее сжатие: {avg_compression:+.2f}%")
        print(f"  Среднее время кодирования: {avg_encode_time:.4f}с")
        print(f"  Среднее время декодирования: {avg_decode_time:.4f}с")
        print(f"  Успешных тестов: {success_rate:.1f}%")

    return results


def save_encoded_files():
    """Сохраняет закодированные версии тестовых файлов для всех алгоритмов"""
    test_dir = Path("compression_tests")

    encoders = {
        'rle': RLEEncoder(),
        'lz78': LZ78Encoder(),
        'lz77': LZ77Encoder()
    }

    print("\nСохранение закодированных файлов:")
    print("=" * 50)

    for algorithm, encoder in encoders.items():
        encoded_dir = Path(f"{algorithm}_encoded")
        encoded_dir.mkdir(exist_ok=True)

        for test_file in test_dir.glob("*.bin"):
            # Читаем исходный файл
            with open(test_file, "rb") as f:
                original_data = f.read()

            # Кодируем
            encoded_data = encoder.encode(original_data)

            # Сохраняем закодированную версию
            encoded_file = encoded_dir / f"{test_file.stem}.{algorithm}"
            with open(encoded_file, "wb") as f:
                f.write(encoded_data)

            print(f"Сохранен: {encoded_file}")


if __name__ == "__main__":
    # Создаем тестовые файлы, если они не существуют
    if not Path("compression_tests").exists():
        print("Создание тестовых файлов...")
        create_test_files()

    # Запускаем тесты для всех алгоритмов
    results = run_compression_tests()

    # Сохраняем закодированные файлы
    save_encoded_files()

    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 80)
    print("Протестированы все три задания:")
    print("1. Л5.1 (RLE) - Наивное RLE сжатие")
    print("2. Л5.2 (LZ78) - LZ78 сжатие")
    print("3. Л5.3 (LZ77) - LZ77 сжатие (бонус)")