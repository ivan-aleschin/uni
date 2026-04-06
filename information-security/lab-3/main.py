"""
Лабораторная работа №3 — Сети Фейстеля (4 ветви)
Вариант 1: 8 раундов, образующая функция "сложение"
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

WORD_SIZE = 32
WORD_MASK = (1 << WORD_SIZE) - 1
BLOCK_SIZE_BYTES = 16  # 128 бит = 16 байт


def rol32(value: int, shift: int) -> int:
    shift %= WORD_SIZE
    return ((value << shift) & WORD_MASK) | (value >> (WORD_SIZE - shift))


def ror32(value: int, shift: int) -> int:
    shift %= WORD_SIZE
    return (value >> shift) | ((value << (WORD_SIZE - shift)) & WORD_MASK)


def split_u128_to_words(block: bytes) -> Tuple[int, int, int, int]:
    if len(block) != BLOCK_SIZE_BYTES:
        raise ValueError("Block size must be 16 bytes (128 bits).")
    x1 = int.from_bytes(block[0:4], "big")
    x2 = int.from_bytes(block[4:8], "big")
    x3 = int.from_bytes(block[8:12], "big")
    x4 = int.from_bytes(block[12:16], "big")
    return x1, x2, x3, x4


def words_to_u128(words: Tuple[int, int, int, int]) -> bytes:
    x1, x2, x3, x4 = words
    return (
        x1.to_bytes(4, "big")
        + x2.to_bytes(4, "big")
        + x3.to_bytes(4, "big")
        + x4.to_bytes(4, "big")
    )


def pkcs7_pad(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded data length.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid padding length.")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding bytes.")
    return data[:-pad_len]


@dataclass
class FeistelParams:
    rounds: int = 8
    f_mode: str = "add"  # "add" or "xor"
    key: int = 0x0123456789ABCDEF  # 64-битный ключ


class Feistel4:
    def __init__(self, params: FeistelParams) -> None:
        self.params = params
        self.k1 = (params.key >> 32) & WORD_MASK
        self.k2 = params.key & WORD_MASK
        if self.params.rounds < 1:
            raise ValueError("Number of rounds must be >= 1.")
        if self.params.f_mode not in {"add", "xor"}:
            raise ValueError("Unsupported f_mode. Use 'add' or 'xor'.")

    def _vi(self, round_index: int) -> int:
        r = round_index % WORD_SIZE
        return (rol32(self.k1, r) + ror32(self.k2, r)) & WORD_MASK

    def _f(self, x1: int, round_index: int) -> int:
        vi = self._vi(round_index)
        if self.params.f_mode == "add":
            return (x1 + vi) & WORD_MASK
        return x1 ^ vi

    def encrypt_block(self, block: bytes, verbose: bool = False) -> bytes:
        x1, x2, x3, x4 = split_u128_to_words(block)
        if verbose:
            print("Блок (X1,X2,X3,X4) на входе:")
            print(f"  {x1:08X} {x2:08X} {x3:08X} {x4:08X}")
        for i in range(1, self.params.rounds + 1):
            f_val = self._f(x1, i)
            new_x1 = x2 ^ f_val
            new_x2 = x3
            new_x3 = x4
            new_x4 = x1
            x1, x2, x3, x4 = new_x1, new_x2, new_x3, new_x4
            if verbose:
                print(f"Раунд {i:02d}: X1={x1:08X} X2={x2:08X} X3={x3:08X} X4={x4:08X}")
        return words_to_u128((x1, x2, x3, x4))

    def decrypt_block(self, block: bytes, verbose: bool = False) -> bytes:
        x1, x2, x3, x4 = split_u128_to_words(block)
        if verbose:
            print("Блок (X1,X2,X3,X4) на входе (для дешифрования):")
            print(f"  {x1:08X} {x2:08X} {x3:08X} {x4:08X}")
        for i in range(self.params.rounds, 0, -1):
            prev_x1 = x4
            prev_x2 = x1 ^ self._f(prev_x1, i)
            prev_x3 = x2
            prev_x4 = x3
            x1, x2, x3, x4 = prev_x1, prev_x2, prev_x3, prev_x4
            if verbose:
                print(f"Раунд {i:02d}: X1={x1:08X} X2={x2:08X} X3={x3:08X} X4={x4:08X}")
        return words_to_u128((x1, x2, x3, x4))

    def encrypt(self, data: bytes, verbose: bool = False) -> bytes:
        padded = pkcs7_pad(data, BLOCK_SIZE_BYTES)
        blocks = [
            padded[i : i + BLOCK_SIZE_BYTES]
            for i in range(0, len(padded), BLOCK_SIZE_BYTES)
        ]
        out = bytearray()
        for idx, blk in enumerate(blocks):
            show = verbose and idx == 0
            out.extend(self.encrypt_block(blk, verbose=show))
        return bytes(out)

    def decrypt(self, data: bytes, verbose: bool = False) -> bytes:
        if len(data) % BLOCK_SIZE_BYTES != 0:
            raise ValueError("Ciphertext length must be multiple of 16 bytes.")
        blocks = [
            data[i : i + BLOCK_SIZE_BYTES]
            for i in range(0, len(data), BLOCK_SIZE_BYTES)
        ]
        out = bytearray()
        for idx, blk in enumerate(blocks):
            show = verbose and idx == 0
            out.extend(self.decrypt_block(blk, verbose=show))
        return pkcs7_unpad(bytes(out), BLOCK_SIZE_BYTES)


def banner(title: str) -> str:
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


def main() -> None:
    params = FeistelParams(
        rounds=8,
        f_mode="add",
        key=0x0123456789ABCDEF,
    )

    cipher = Feistel4(params)

    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, "input.txt")
    encrypted_file = os.path.join(base_dir, "encrypted.txt")
    decrypted_file = os.path.join(base_dir, "decrypted.txt")

    if not os.path.exists(input_file):
        sample = "Сеть Фейстеля, 4 ветви, 8 раундов. Вариант 1."
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(sample)

    with open(input_file, "r", encoding="utf-8") as f:
        plaintext = f.read()

    print(banner("ПАРАМЕТРЫ АЛГОРИТМА"))
    print(f"Раунды: {params.rounds}")
    print(f"Образующая функция: {params.f_mode}")
    print(f"Ключ (64 бита): 0x{params.key:016X}")
    print(f"K1=0x{cipher.k1:08X}, K2=0x{cipher.k2:08X}")

    print(banner("ИСХОДНЫЙ ТЕКСТ"))
    print(plaintext)

    print(banner("ДЕТАЛЬНАЯ ДЕМОНСТРАЦИЯ (ПЕРВЫЙ БЛОК)"))
    encrypted = cipher.encrypt(plaintext.encode("utf-8"), verbose=True)

    print(banner("КРИПТОГРАММА (HEX)"))
    encrypted_hex = encrypted.hex()
    print(encrypted_hex)

    with open(encrypted_file, "w", encoding="utf-8") as f:
        f.write(encrypted_hex)

    print(banner("ДЕШИФРОВАНИЕ (ПЕРВЫЙ БЛОК)"))
    decrypted = cipher.decrypt(encrypted, verbose=True)
    decrypted_text = decrypted.decode("utf-8")

    with open(decrypted_file, "w", encoding="utf-8") as f:
        f.write(decrypted_text)

    print(banner("РАСШИФРОВАННЫЙ ТЕКСТ"))
    print(decrypted_text)

    print(banner("СРАВНЕНИЕ"))
    print(f"Совпадение: {'да' if plaintext == decrypted_text else 'нет'}")


if __name__ == "__main__":
    main()
