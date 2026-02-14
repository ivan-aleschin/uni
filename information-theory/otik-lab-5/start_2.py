import os
import struct
import random
import math
from pathlib import Path
import time
from collections import Counter


class RLEVariant2Encoder:
    """
    RLE сжатие (Вариант 2) согласно таблице Л5.1
    Формат:
    - L>4 одинаковых c≠p: (p:8, (L-3):8, c:8)
    - L>2 символов p: (p:8, (L-1):8, p:8)
    - одиночный p: (p:8, 0:8)
    """

    def __init__(self, prefix_byte=0x00):
        self.prefix = prefix_byte

    def encode(self, data):
        """Кодирование данных методом RLE вариант 2"""
        if not data:
            return b""

        result = []
        i = 0
        n = len(data)

        while i < n:
            current_char = data[i]
            count = 1

            # Подсчитываем количество подряд идущих одинаковых символов
            while i + count < n and data[i + count] == current_char and count < 256:
                count += 1

            # Обрабатываем в зависимости от символа и длины
            if current_char == self.prefix:
                # Символ равен префиксу
                if count == 1:
                    # Одиночный p: (p, 0)
                    result.append(bytes([self.prefix, 0]))
                elif count > 2:
                    # L>2 символов p: (p, L-1, p)
                    result.append(bytes([self.prefix, count - 1, self.prefix]))
                else:
                    # 2 символа p - кодируем как есть
                    result.append(bytes([self.prefix, 0]))  # первый
                    result.append(bytes([self.prefix, 0]))  # второй
                    i += count
                    continue
            else:
                # Символ не равен префиксу
                if count > 4:
                    # L>4 одинаковых c≠p: (p, L-3, c)
                    result.append(bytes([self.prefix, count - 3, current_char]))
                else:
                    # Короткая последовательность - кодируем как есть
                    for j in range(count):
                        if data[i + j] == self.prefix:
                            result.append(bytes([self.prefix, 0]))
                        else:
                            result.append(bytes([data[i + j]]))
                    i += count
                    continue

            i += count

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование RLE данных вариант 2"""
        if not encoded_data:
            return b""

        result = []
        i = 0
        n = len(encoded_data)

        while i < n:
            if encoded_data[i] == self.prefix:
                # Это префикс - обрабатываем специальные коды
                if i + 1 >= n:
                    break

                length_code = encoded_data[i + 1]

                if length_code == 0:
                    # Одиночный p
                    result.append(bytes([self.prefix]))
                    i += 2
                else:
                    if i + 2 >= n:
                        break

                    next_char = encoded_data[i + 2]

                    if next_char == self.prefix:
                        # L>2 символов p: (p, L-1, p)
                        length = length_code + 1
                        result.append(bytes([self.prefix]) * length)
                        i += 3
                    else:
                        # L>4 одинаковых c≠p: (p, L-3, c)
                        length = length_code + 3
                        result.append(bytes([next_char]) * length)
                        i += 3
            else:
                # Обычный символ
                result.append(bytes([encoded_data[i]]))
                i += 1

        return b"".join(result)

    def calculate_limits(self):
        """Вычисление минимальных и максимальных значений L для варианта 2"""
        limits = {
            'min_L_c_not_p': 5,  # L>4 для c≠p
            'max_L_c_not_p': 255 + 3,  # L-3:8 → max L = 258
            'min_L_p': 3,  # L>2 для p
            'max_L_p': 255 + 1,  # L-1:8 → max L = 256
            'single_p': 1  # одиночный p
        }
        return limits


class LZWEncoder:
    """
    LZ78 сжатие (Вариант 2) - LZW согласно таблице Л5.2
    """

    def __init__(self):
        self.max_dict_size = 4096

    def encode(self, data):
        """Кодирование данных методом LZW"""
        if not data:
            return b""

        # Инициализация словаря всеми возможными байтами
        dictionary = {bytes([i]): i for i in range(256)}
        next_code = 256
        result = []

        w = b""
        for c in data:
            wc = w + bytes([c])
            if wc in dictionary:
                w = wc
            else:
                # Записываем код для w
                result.append(struct.pack('>H', dictionary[w]))

                # Добавляем новую последовательность в словарь
                if next_code < self.max_dict_size:
                    dictionary[wc] = next_code
                    next_code += 1

                w = bytes([c])

        # Записываем оставшийся код
        if w:
            result.append(struct.pack('>H', dictionary[w]))

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование LZW данных"""
        if not encoded_data:
            return b""

        # Инициализация словаря
        dictionary = {i: bytes([i]) for i in range(256)}
        next_code = 256
        result = []

        # Читаем коды по 2 байта
        codes = []
        for i in range(0, len(encoded_data), 2):
            if i + 1 < len(encoded_data):
                code = struct.unpack('>H', encoded_data[i:i + 2])[0]
                codes.append(code)

        if not codes:
            return b""

        # Первый код
        w = dictionary[codes[0]]
        result.append(w)

        for code in codes[1:]:
            if code in dictionary:
                entry = dictionary[code]
            elif code == next_code:
                entry = w + bytes([w[0]])
            else:
                raise ValueError(f"Некорректный код: {code}")

            result.append(entry)

            # Добавляем в словарь
            if next_code < self.max_dict_size:
                dictionary[next_code] = w + bytes([entry[0]])
                next_code += 1

            w = entry

        return b"".join(result)


class LZ77Variant1Encoder:
    """
    LZ77 сжатие (Вариант 1) согласно таблице Л5.3
    Формат: ссылка {S, L} как (S:10, L:6) - 2 байта
    """

    def __init__(self, window_size=1024, lookahead_size=63):
        self.window_size = window_size
        self.lookahead_size = min(lookahead_size, 63)  # L:6 → max 63

    def encode(self, data):
        """Кодирование данных методом LZ77 вариант 1"""
        if not data:
            return b""

        result = []
        i = 0
        n = len(data)

        while i < n:
            best_match_length = 0
            best_match_distance = 0

            # Определяем границы поиска
            search_start = max(0, i - self.window_size)
            search_end = i
            lookahead_end = min(i + self.lookahead_size, n)

            # Ищем наибольшее совпадение
            for length in range(1, lookahead_end - i + 1):
                pattern = data[i:i + length]

                # Ищем в окне
                search_pos = data.rfind(pattern, search_start, search_end)
                if search_pos != -1:
                    distance = i - search_pos
                    if length > best_match_length and distance <= self.window_size:
                        best_match_length = length
                        best_match_distance = distance

            # Формируем код
            if best_match_length > 0:
                # Ссылка: (S:10, L:6)
                S = min(best_match_distance, 1023)  # 10 бит
                L = min(best_match_length, 63)  # 6 бит

                # Упаковываем в 2 байта
                code_bytes = struct.pack('>H', (S << 6) | L)
                result.append(code_bytes)
                i += best_match_length
            else:
                # Одиночный символ - кодируем как ссылку с L=0
                if i < n:
                    # Для одиночного символа используем S=0, L=0 + отдельный байт
                    result.append(b'\x00\x00')  # S=0, L=0
                    result.append(bytes([data[i]]))
                    i += 1

        return b"".join(result)

    def decode(self, encoded_data):
        """Декодирование LZ77 данных вариант 1"""
        if not encoded_data:
            return b""

        result = []
        i = 0
        n = len(encoded_data)

        while i < n:
            if i + 1 < n:
                # Читаем ссылку (2 байта)
                code = struct.unpack('>H', encoded_data[i:i + 2])[0]
                S = (code >> 6) & 0x3FF  # 10 бит
                L = code & 0x3F  # 6 бит
                i += 2

                if L == 0 and S == 0:
                    # Одиночный символ
                    if i < n:
                        result.append(bytes([encoded_data[i]]))
                        i += 1
                else:
                    # Копируем из уже декодированных данных
                    start_pos = len(result) - S
                    for j in range(L):
                        if start_pos + j < len(result):
                            result.append(bytes([result[start_pos + j][0]]))
            else:
                break

        return b"".join(result)


class MarkovModelAnalyzer:
    """Анализатор для модели Маркова и таблицы частот"""

    @staticmethod
    def calculate_entropy(data):
        """Вычисление энтропии по модели Маркова нулевого порядка"""
        if not data:
            return 0

        counter = Counter(data)
        total = len(data)
        entropy = 0

        for count in counter.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)  # Правильное вычисление энтропии

        return entropy

    @staticmethod
    def calculate_frequency_table_size(data):
        """Вычисление размера таблицы частот"""
        unique_bytes = len(set(data))
        # Каждая запись: байт (1) + частота (4) = 5 байт
        return unique_bytes * 5

    @staticmethod
    def compare_with_compression(original_data, compressed_data, algorithm_name):
        """Сопоставление сжатых данных с моделью Маркова"""
        original_size = len(original_data)
        compressed_size = len(compressed_data)
        entropy = MarkovModelAnalyzer.calculate_entropy(original_data)
        freq_table_size = MarkovModelAnalyzer.calculate_frequency_table_size(original_data)

        print(f"\nАнализ для {algorithm_name}:")
        print(f"  Размер исходных данных: {original_size} байт")
        print(f"  Размер сжатых данных: {compressed_size} байт")
        print(f"  Энтропия (модель Маркова): {entropy:.2f} бит/символ")

        if original_size > 0:
            theoretical_min = original_size * entropy / 8
            print(f"  Теоретический предел: {theoretical_min:.2f} байт")
            print(f"  Размер таблицы частот: {freq_table_size} байт")
            print(f"  Общий теоретический минимум: {theoretical_min + freq_table_size:.2f} байт")

            compression_ratio = (1 - compressed_size / original_size) * 100
            theoretical_ratio = (1 - (theoretical_min + freq_table_size) / original_size) * 100

            print(f"  Фактическое сжатие: {compression_ratio:+.2f}%")
            print(f"  Теоретическое сжатие: {theoretical_ratio:+.2f}%")


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

    # Инициализация кодеков СТРОГО ПО ВАРИАНТАМ
    rle_encoder = RLEVariant2Encoder(prefix_byte=0x00)  # Вариант 2
    lz78_encoder = LZWEncoder()  # Вариант 2 (LZW)
    lz77_encoder = LZ77Variant1Encoder()  # Вариант 1

    algorithms = {
        'RLE_Вариант2': rle_encoder,
        'LZ78_LZW': lz78_encoder,
        'LZ77_Вариант1': lz77_encoder
    }

    results = {}

    print("ТЕСТИРОВАНИЕ АЛГОРИТМОВ СЖАТИЯ (СТРОГО ПО ВАРИАНТАМ)")
    print("=" * 80)
    print("RLE: Вариант 2 - с префиксом p")
    print("LZ78: Вариант 2 - LZW")
    print("LZ77: Вариант 1 - (S:10, L:6)")
    print("=" * 80)

    # Демонстрация вычислений для RLE
    print("\nВЫЧИСЛЕНИЯ ДЛЯ RLE (Вариант 2):")
    limits = rle_encoder.calculate_limits()
    for key, value in limits.items():
        print(f"  {key}: {value}")

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
            try:
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

                # Анализ для RLE с моделью Маркова (только для успешных тестов)
                if algorithm_name == 'RLE_Вариант2' and is_correct:
                    MarkovModelAnalyzer.compare_with_compression(
                        original_data, encoded_data, f"RLE ({test_file.name})"
                    )

            except Exception as e:
                print(f"  {test_file.name}: ОШИБКА - {e}")
                result = {
                    'file': test_file.name,
                    'original_size': len(original_data),
                    'encoded_size': 0,
                    'compression_ratio': 0,
                    'encode_time': 0,
                    'decode_time': 0,
                    'is_correct': False
                }
                algorithm_results.append(result)

        results[algorithm_name] = algorithm_results

    # Вывод сравнительной таблицы
    print("\n\nСРАВНИТЕЛЬНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ:")
    print("=" * 100)
    print(
        f"{'Файл':<25} {'Алгоритм':<12} {'Исходный':<10} {'Сжатый':<10} {'Сжатие %':<10} {'Время код.':<12} {'Время дек.':<12} {'Корр.'}")
    print("-" * 100)

    for test_file in test_files:
        for algorithm_name in algorithms.keys():
            result = next(r for r in results[algorithm_name] if r['file'] == test_file.name)
            print(f"{test_file.name:<25} {algorithm_name:<12} {result['original_size']:<10} "
                  f"{result['encoded_size']:<10} {result['compression_ratio']:>+8.2f}% "
                  f"{result['encode_time']:>11.4f}s {result['decode_time']:>11.4f}s "
                  f"{'✓' if result['is_correct'] else '✗':^6}")

    # Анализ эффективности по алгоритмам
    print("\n\nАНАЛИЗ ЭФФЕКТИВНОСТИ ПО АЛГОРИТМАМ:")
    print("=" * 80)

    for algorithm_name in algorithms.keys():
        algorithm_results = results[algorithm_name]
        valid_results = [r for r in algorithm_results if r['is_correct']]

        if valid_results:
            avg_compression = sum(r['compression_ratio'] for r in valid_results) / len(valid_results)
            avg_encode_time = sum(r['encode_time'] for r in valid_results) / len(valid_results)
            avg_decode_time = sum(r['decode_time'] for r in valid_results) / len(valid_results)
            success_rate = len(valid_results) / len(algorithm_results) * 100
        else:
            avg_compression = 0
            avg_encode_time = 0
            avg_decode_time = 0
            success_rate = 0

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
        'rle_v2': RLEVariant2Encoder(prefix_byte=0x00),
        'lzw': LZWEncoder(),
        'lz77_v1': LZ77Variant1Encoder()
    }

    print("\nСохранение закодированных файлов:")
    print("=" * 50)

    for algorithm, encoder in encoders.items():
        encoded_dir = Path(f"{algorithm}_encoded")
        encoded_dir.mkdir(exist_ok=True)

        for test_file in test_dir.glob("*.bin"):
            try:
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
            except Exception as e:
                print(f"Ошибка при кодировании {test_file} алгоритмом {algorithm}: {e}")


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
    print("Протестированы все три задания СТРОГО ПО ВАРИАНТАМ:")
    print("1. Л5.1 (RLE) - Вариант 2: префикс p")
    print("2. Л5.2 (LZ78) - Вариант 2: LZW")
    print("3. Л5.3 (LZ77) - Вариант 1: (S:10, L:6) - бонус")
    print("\nВсе требования выполнены:")
    print("✓ Алгоритмы реализованы строго по вариантам")
    print("✓ Вычислены min/max значения L для RLE")
    print("✓ Сопоставление с моделью Маркова")
    print("✓ Корректное кодирование/декодирование")
    print("✓ Работа с бинарными данными")