import argparse
import logging
import struct
from pathlib import Path
from collections import Counter
import heapq
import math

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

SIGNATURE = b"PIN31_5_ARC"
VERSION = (2, 0)
ALG_NONE = 0
ALG_HUFFMAN = 1
ALG_ARITHMETIC = 2
ALG_SHANNON = 3


class HuffmanNode:
    def __init__(self, char, freq):
        self.char, self.freq, self.left, self.right = char, freq, None, None

    def __lt__(self, other):
        return self.freq < other.freq


class BitStream:
    def __init__(self):
        self.buffer = bytearray()
        self.current_byte = 0
        self.bit_count = 0

    def write_bit(self, bit):
        self.current_byte = (self.current_byte << 1) | bit
        self.bit_count += 1
        if self.bit_count == 8:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_count = 0

    def get_bytes(self):
        if self.bit_count > 0:
            self.buffer.append(self.current_byte << (8 - self.bit_count))
        return bytes(self.buffer)


class BitReader:
    def __init__(self, data):
        self.data = data
        self.byte_index = 0
        self.bit_index = 0

    def read_bit(self):
        if self.byte_index >= len(self.data):
            return 0
        byte = self.data[self.byte_index]
        bit = (byte >> (7 - self.bit_index)) & 1
        self.bit_index += 1
        if self.bit_index == 8:
            self.bit_index = 0
            self.byte_index += 1
        return bit


def huffman_compress(data):
    if not data:
        return b"", b""
    freqs = Counter(data)
    pq = [HuffmanNode(char, freq) for char, freq in freqs.items()]
    heapq.heapify(pq)
    while len(pq) > 1:
        left, right = heapq.heappop(pq), heapq.heappop(pq)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heapq.heappush(pq, merged)
    root = pq[0] if pq else None
    codes = {}

    def generate_codes(node, code=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = code
            return
        generate_codes(node.left, code + "0")
        generate_codes(node.right, code + "1")

    generate_codes(root)
    if not codes and freqs:
        codes = {list(freqs.keys())[0]: "0"}
    encoded_data_str = "".join(codes[char] for char in data)
    padding = 8 - len(encoded_data_str) % 8
    if padding == 8:
        padding = 0
    encoded_data_str += "0" * padding
    encoded_bytes = bytearray(
        int(encoded_data_str[i : i + 8], 2) for i in range(0, len(encoded_data_str), 8)
    )
    freq_table_bytes = b"".join(struct.pack("<BQ", c, f) for c, f in freqs.items())
    return bytes(encoded_bytes), freq_table_bytes


def huffman_decompress(compressed_data, freq_table, original_size):
    if original_size == 0:
        return b""
    freqs = {
        struct.unpack("<B", freq_table[i : i + 1])[0]: struct.unpack(
            "<Q", freq_table[i + 1 : i + 9]
        )[0]
        for i in range(0, len(freq_table), 9)
    }
    pq = [HuffmanNode(char, freq) for char, freq in freqs.items()]
    heapq.heapify(pq)
    if not pq:
        return b""
    while len(pq) > 1:
        left, right = heapq.heappop(pq), heapq.heappop(pq)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heapq.heappush(pq, merged)
    root = pq[0]
    if root.char is not None:
        return bytes([root.char] * original_size)
    bit_string = "".join(f"{byte:08b}" for byte in compressed_data)
    decoded_data, current_node = bytearray(), root
    for bit in bit_string:
        current_node = current_node.left if bit == "0" else current_node.right
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            if len(decoded_data) == original_size:
                break
            current_node = root
    return bytes(decoded_data)


def arithmetic_compress(data, num_bits=32):
    if not data:
        return b"", b""

    freqs = Counter(data)
    total_freq = len(data)

    cum_freqs = {0: 0}
    current_sum = 0
    for i in range(256):
        current_sum += freqs.get(i, 0)
        cum_freqs[i + 1] = current_sum

    max_range = 1 << num_bits
    low, high = 0, max_range - 1
    pending_bits = 0

    stream = BitStream()

    for byte in data:
        code_range = high - low + 1
        high = low + (code_range * cum_freqs[byte + 1]) // total_freq - 1
        low = low + (code_range * cum_freqs[byte]) // total_freq

        while True:
            if high < (max_range // 2):  # E1: интервал в нижней половине
                stream.write_bit(0)
                for _ in range(pending_bits):
                    stream.write_bit(1)
                pending_bits = 0
            elif low >= (max_range // 2):  # E2: интервал в верхней половине
                stream.write_bit(1)
                for _ in range(pending_bits):
                    stream.write_bit(0)
                pending_bits = 0
                low -= max_range // 2
                high -= max_range // 2
            elif low >= (max_range // 4) and high < (
                3 * max_range // 4
            ):  # E3: интервал посередине
                pending_bits += 1
                low -= max_range // 4
                high -= max_range // 4
            else:
                break

            low *= 2
            high = high * 2 + 1

    # Завершение
    pending_bits += 1
    if low < (max_range // 4):
        stream.write_bit(0)
        for _ in range(pending_bits):
            stream.write_bit(1)
    else:
        stream.write_bit(1)
        for _ in range(pending_bits):
            stream.write_bit(0)

    freq_table_bytes = b"".join(struct.pack("<BQ", c, f) for c, f in freqs.items())
    return stream.get_bytes(), freq_table_bytes


def arithmetic_decompress(compressed_data, freq_table, original_size, num_bits=32):
    if original_size == 0:
        return b""

    freqs = {
        struct.unpack("<B", freq_table[i : i + 1])[0]: struct.unpack(
            "<Q", freq_table[i + 1 : i + 9]
        )[0]
        for i in range(0, len(freq_table), 9)
    }
    total_freq = sum(freqs.values())

    cum_freqs = {0: 0}
    freq_map = {}
    current_sum = 0
    for i in range(256):
        current_sum += freqs.get(i, 0)
        cum_freqs[i + 1] = current_sum
        if freqs.get(i, 0) > 0:
            freq_map[i] = (cum_freqs[i], cum_freqs[i + 1])

    reader = BitReader(compressed_data)
    max_range = 1 << num_bits
    low, high = 0, max_range - 1

    value = 0
    for _ in range(num_bits):
        value = (value << 1) | reader.read_bit()

    decoded_data = bytearray()
    for _ in range(original_size):
        code_range = high - low + 1
        current_freq = ((value - low + 1) * total_freq - 1) // code_range

        char_code = -1
        for code, (start_freq, end_freq) in freq_map.items():
            if start_freq <= current_freq < end_freq:
                char_code = code
                break

        decoded_data.append(char_code)

        high = low + (code_range * cum_freqs[char_code + 1]) // total_freq - 1
        low = low + (code_range * cum_freqs[char_code]) // total_freq

        while True:
            if high < (max_range // 2):  # E1
                pass
            elif low >= (max_range // 2):  # E2
                value -= max_range // 2
                low -= max_range // 2
                high -= max_range // 2
            elif low >= (max_range // 4) and high < (3 * max_range // 4):  # E3
                value -= max_range // 4
                low -= max_range // 4
                high -= max_range // 4
            else:
                break

            low *= 2
            high = high * 2 + 1
            value = (value << 1) | reader.read_bit()

    return bytes(decoded_data)


def shannon_compress(data):
    # (Код Шеннона остается без изменений)
    if not data:
        return b"", b""
    freqs = Counter(data)
    total_freq = len(data)
    sorted_freqs = sorted(freqs.items(), key=lambda item: item[1], reverse=True)
    codes, cum_prob = {}, 0.0
    for char, freq in sorted_freqs:
        prob = freq / total_freq
        length = math.ceil(-math.log2(prob) if prob > 0 else 0)
        code_val, temp_cum = 0, cum_prob
        for i in range(length):
            temp_cum *= 2
            if temp_cum >= 1:
                code_val |= 1 << (length - 1 - i)
                temp_cum -= 1
        codes[char] = f"{code_val:0{length}b}" if length > 0 else ""
        cum_prob += prob
    encoded_data_str = "".join(codes[char] for char in data)
    padding = 8 - len(encoded_data_str) % 8
    if padding == 8:
        padding = 0
    encoded_data_str += "0" * padding
    encoded_bytes = bytearray(
        int(encoded_data_str[i : i + 8], 2) for i in range(0, len(encoded_data_str), 8)
    )
    freq_table_bytes = b"".join(struct.pack("<BQ", c, f) for c, f in freqs.items())
    return bytes(encoded_bytes), freq_table_bytes


def shannon_decompress(compressed_data, freq_table, original_size):
    # (Код Шеннона остается без изменений)
    if original_size == 0:
        return b""
    freqs = {
        struct.unpack("<B", freq_table[i : i + 1])[0]: struct.unpack(
            "<Q", freq_table[i + 1 : i + 9]
        )[0]
        for i in range(0, len(freq_table), 9)
    }
    total_freq = sum(freqs.values())
    sorted_freqs = sorted(freqs.items(), key=lambda item: item[1], reverse=True)
    codes, cum_prob = {}, 0.0
    for char, freq in sorted_freqs:
        prob = freq / total_freq
        length = math.ceil(-math.log2(prob) if prob > 0 else 0)
        code_val, temp_cum = 0, cum_prob
        for i in range(length):
            temp_cum *= 2
            if temp_cum >= 1:
                code_val |= 1 << (length - 1 - i)
                temp_cum -= 1
        codes[f"{code_val:0{length}b}" if length > 0 else ""] = char
        cum_prob += prob
    bit_string = "".join(f"{byte:08b}" for byte in compressed_data)
    decoded_data, current_code = bytearray(), ""
    for bit in bit_string:
        current_code += bit
        if current_code in codes:
            decoded_data.append(codes[current_code])
            if len(decoded_data) == original_size:
                break
            current_code = ""
    return bytes(decoded_data)


COMPRESSORS = {
    ALG_HUFFMAN: huffman_compress,
    ALG_ARITHMETIC: arithmetic_compress,
    ALG_SHANNON: shannon_compress,
}
DECOMPRESSORS = {
    ALG_HUFFMAN: huffman_decompress,
    ALG_ARITHMETIC: arithmetic_decompress,
    ALG_SHANNON: shannon_decompress,
}


def encode(input_path: Path, output_file: Path, algorithm: int, force: bool):
    logging.info(
        f"Начало кодирования: '{input_path}' -> '{output_file}' с алгоритмом {algorithm}"
    )
    if not input_path.exists():
        logging.error(f"Ошибка: Путь не существует: {input_path}")
        return
    if input_path.is_file():
        files_to_archive, base_dir = [input_path], input_path.parent
    else:
        files_to_archive, base_dir = (
            [p for p in input_path.rglob("*") if p.is_file()],
            input_path,
        )
    if not files_to_archive:
        logging.warning("Файлы для архивации не найдены.")
        return
    all_files_metadata, all_files_data_blocks = [], []
    logging.info(f"Найдено {len(files_to_archive)} файлов. Обработка...")
    for file_path in files_to_archive:
        original_data, original_size = file_path.read_bytes(), file_path.stat().st_size
        current_alg, compressed_data, freq_table = algorithm, b"", b""
        if algorithm in COMPRESSORS:
            compressed_data, freq_table = COMPRESSORS[algorithm](original_data)
            if not force and (len(compressed_data) + len(freq_table)) >= original_size:
                logging.warning(
                    f"Сжатие неэффективно для '{file_path}'. Сохраняется без сжатия."
                )
                current_alg, compressed_data, freq_table = ALG_NONE, original_data, b""
        else:
            current_alg, compressed_data = ALG_NONE, original_data
        all_files_metadata.append({
            "relative_path": file_path.relative_to(base_dir),
            "original_size": original_size,
            "algorithm": current_alg,
            "freq_table": freq_table,
            "compressed_size": len(compressed_data),
        })
        all_files_data_blocks.append(compressed_data)
    try:
        with output_file.open("wb") as f_out:
            f_out.write(SIGNATURE)
            f_out.write(struct.pack("<BB", *VERSION))
            f_out.write(b"\x00" * 3)
            f_out.write(struct.pack("<Q", len(files_to_archive)))
            for meta in all_files_metadata:
                path_bytes = str(meta["relative_path"]).encode("utf-8")
                f_out.write(struct.pack("<Q", meta["original_size"]))
                f_out.write(struct.pack("<H", len(path_bytes)))
                f_out.write(path_bytes)
                f_out.write(struct.pack("<B", meta["algorithm"]))
                f_out.write(struct.pack("<I", len(meta["freq_table"])))
                f_out.write(meta["freq_table"])
                f_out.write(struct.pack("<Q", meta["compressed_size"]))
            for data_block in all_files_data_blocks:
                f_out.write(data_block)
    except IOError as e:
        logging.error(f"Ошибка записи в архив: {e}")
        return
    logging.info("Архивация успешно завершена.")


def decode(input_file: Path, output_dir: Path):
    logging.info(f"Начало декодирования: '{input_file}' -> '{output_dir}'")
    try:
        with input_file.open("rb") as f_in:
            if f_in.read(len(SIGNATURE)) != SIGNATURE:
                raise ValueError("Неверная сигнатура")
            major, minor = struct.unpack("<BB", f_in.read(2))
            logging.info(f"Версия архива: {major}.{minor}")
            if major != VERSION[0]:
                raise ValueError(f"Неподдерживаемая версия {major}")
            f_in.read(3)
            num_files = struct.unpack("<Q", f_in.read(8))[0]
            logging.info(f"Архив содержит {num_files} файлов.")
            metadata = []
            for i in range(num_files):
                original_size, path_len = (
                    struct.unpack("<Q", f_in.read(8))[0],
                    struct.unpack("<H", f_in.read(2))[0],
                )
                path_str, alg, table_size = (
                    f_in.read(path_len).decode("utf-8"),
                    struct.unpack("<B", f_in.read(1))[0],
                    struct.unpack("<I", f_in.read(4))[0],
                )
                freq_table, compressed_size = (
                    f_in.read(table_size),
                    struct.unpack("<Q", f_in.read(8))[0],
                )
                metadata.append({
                    "path": Path(path_str),
                    "original_size": original_size,
                    "algorithm": alg,
                    "freq_table": freq_table,
                    "compressed_size": compressed_size,
                })
                logging.debug(
                    f"  Прочитаны метаданные для '{path_str}' (алгоритм: {alg})"
                )
            for meta in metadata:
                dest_path = output_dir / meta["path"]
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                compressed_data = f_in.read(meta["compressed_size"])
                if meta["algorithm"] == ALG_NONE:
                    decoded_data = compressed_data
                elif meta["algorithm"] in DECOMPRESSORS:
                    decoded_data = DECOMPRESSORS[meta["algorithm"]](
                        compressed_data, meta["freq_table"], meta["original_size"]
                    )
                else:
                    logging.error(
                        f"Неизвестный алгоритм сжатия: {meta['algorithm']} для файла '{meta['path']}'"
                    )
                    continue
                dest_path.write_bytes(decoded_data)
                logging.info(f"Файл '{dest_path}' успешно распакован.")
    except (IOError, ValueError, struct.error) as e:
        logging.error(f"Критическая ошибка при декодировании: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Архиватор с поддержкой сжатия (ЛР4).")
    parser.add_argument("mode", choices=["encode", "decode"], help="Режим работы")
    parser.add_argument("input", type=Path, help="Исходный путь")
    parser.add_argument("output", type=Path, help="Результирующий путь")
    parser.add_argument(
        "-a",
        "--algorithm",
        default="huffman",
        choices=["none", "huffman", "arithmetic", "shannon"],
        help="Алгоритм сжатия",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Принудительное сжатие, даже если оно неэффективно.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Включить подробное логирование."
    )
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    alg_map = {
        "none": ALG_NONE,
        "huffman": ALG_HUFFMAN,
        "arithmetic": ALG_ARITHMETIC,
        "shannon": ALG_SHANNON,
    }
    if args.mode == "encode":
        encode(args.input, args.output, alg_map[args.algorithm], args.force)
    elif args.mode == "decode":
        args.output.mkdir(parents=True, exist_ok=True)
        decode(args.input, args.output)
