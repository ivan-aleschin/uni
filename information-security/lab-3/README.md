# Отчет по лабораторной работе № 3

**Тема:** СЕТИ ФЕЙСТЕЛЯ  
**Дисциплина:** Защита информации  
**Вариант:** 1 (8 раундов, образующая функция — «сложение»)

---

## 1. Задание

1. Выбрать параметры сети Фейстеля по варианту.  
2. Разработать программу шифрования и дешифрования текста.  
3. Выполнить шифрование исходного текста, получить криптограмму, выполнить дешифрование и сравнить с исходным текстом.  
4. Оформить результаты в виде отчета.  
5. Содержание отчета:  
   - описание используемого метода;  
   - описание исходных данных;  
   - алгоритм работы программы;  
   - текст программы;  
   - результаты работы программы;  
   - анализ результатов;  
   - выводы.

**Вариант 1:**  
- Количество раундов: **8**  
- Образующая функция: **сложение**  
- Возможность изменять количество раундов и тип F предусмотрена в коде.  
  Настройка выполняется в `FeistelParams`: параметр `rounds` задает число раундов, а `f_mode` принимает значения `add` или `xor`.

---

## 2. Теория

### 2.1. Сеть Фейстеля (классическая)

Сеть Фейстеля — метод построения блочных шифров, преобразующий n-битный блок открытого текста в n-битный блок шифртекста.  
Классическая структура содержит **две ветви**, и на каждом раунде выполняются:
1. Вычисление функции F от одной ветви и параметра Vᵢ.  
2. Наложение результата на другую ветвь через XOR.  
3. Перестановка ветвей.

Ключевое свойство: **обратимость**, даже если F необратима. Дешифрование выполняется тем же алгоритмом, но с параметрами Vᵢ в обратном порядке.

### 2.2. Модифицированная сеть (4 ветви)

При блоке 128 бит удобно разбить данные на 4 ветви по 32 бита.  
Пусть входной блок:

**X1 X2 X3 X4**

Итеративные формулы (i = 1..n):

- **X1(i) = X2(i−1) ⊕ F(X1(i−1), Vᵢ)**  
- **X2(i) = X3(i−1)**  
- **X3(i) = X4(i−1)**  
- **X4(i) = X1(i−1)**

### 2.3. Образующая функция

Для варианта 1 используется функция «сложение» внутри F:

- **F(X1, Vᵢ) = X1 + Vᵢ**  
- **Vᵢ = ROL(K1, i) + ROR(K2, i)**

Где:
- **K1, K2** — 32-битные части 64-битного ключа.  
- **ROL/ROR** — циклические сдвиги.

---

## 3. Исходные данные

- Размер блока: **128 бит**  
- Размер ключа: **64 бита**  
- Число раундов (вариант 1): **8**  
- F-режим: **add** (сложение)  
- Ключ по умолчанию: `0x0123456789ABCDEF`  
- Файлы:
  - `input.txt` — исходный текст  
  - `encrypted.txt` — криптограмма (hex)  
  - `decrypted.txt` — расшифрованный текст  

---

## 4. Алгоритм работы программы

1. Чтение текста из `input.txt`.  
2. Разбиение на блоки по 16 байт.  
3. Дополнение PKCS#7, если длина не кратна 16.  
4. Шифрование каждого блока 8 раундами сети Фейстеля.  
5. Запись криптограммы в `encrypted.txt` (hex).  
6. Дешифрование тем же алгоритмом.  
7. Сравнение результата с исходным текстом.

---

## 5. Полный текст программы

```uni/information-security/lab-3/main.py#L1-L220
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
```

---

## 6. Демонстрация (минималистичная и подробная)

Программа выводит:

- параметры алгоритма,  
- исходный текст,  
- раунды первого блока (все 8),  
- криптограмму (hex),  
- раунды расшифровки первого блока,  
- итоговый текст,  
- сравнение.

Без смайликов и слов «УСПЕХ».

---

## 7. Пример запуска (nix-shell)

```uni/information-security/lab-3/README.md#L300-L320
$ cd information-security/lab-3
$ python3 main.py
```

---

## 8. Результаты работы программы

Фактический вывод (пример):

```uni/information-security/lab-3/README.md#L330-L420
========================================================================
ПАРАМЕТРЫ АЛГОРИТМА
========================================================================
Раунды: 8
Образующая функция: add
Ключ (64 бита): 0x0123456789ABCDEF
K1=0x01234567, K2=0x89ABCDEF

========================================================================
ИСХОДНЫЙ ТЕКСТ
========================================================================
Сеть Фейстеля, 4 ветви, 8 раундов.
Лабораторная работа №3, вариант 1.

========================================================================
ДЕТАЛЬНАЯ ДЕМОНСТРАЦИЯ (ПЕРВЫЙ БЛОК)
========================================================================
Блок (X1,X2,X3,X4) на входе:
  D0A1D0B5 D182D18C 20D0A4D0 B5D0B9D1
Раунд 01: X1=463C93F6 X2=20D0A4D0 X3=B5D0B9D1 X4=D0A1D0B5
Раунд 02: X1=0DE439DD X2=B5D0B9D1 X3=D0A1D0B5 X4=463C93F6
Раунд 03: X1=BDE36703 X2=D0A1D0B5 X3=463C93F6 X4=0DE439DD
Раунд 04: X1=1813AAE4 X2=463C93F6 X3=0DE439DD X4=BDE36703
Раунд 05: X1=FEF525C5 X2=0DE439DD X3=BDE36703 X4=1813AAE4
Раунд 06: X1=08091761 X2=BDE36703 X3=1813AAE4 X4=FEF525C5
Раунд 07: X1=C55C457F X2=1813AAE4 X3=FEF525C5 X4=08091761
Раунд 08: X1=C038F2A9 X2=FEF525C5 X3=08091761 X4=C55C457F

========================================================================
КРИПТОГРАММА (HEX)
========================================================================
c038f2a9fef525c508091761c55c457fea46a51a8f320265fd3373332850d1fa6e067cb09e7e054d307b7b45aebc2f47c644f7b9092da1db473e3a5e7d4fc0287979ed5b0b2455854ff969f3184b145a177b60456336fa6137f80a8a210a6bd21f87c3299bf39954abf1cd389f1d74ebe066d94705266990dadc524f9d849fd0

========================================================================
ДЕШИФРОВАНИЕ (ПЕРВЫЙ БЛОК)
========================================================================
Блок (X1,X2,X3,X4) на входе (для дешифрования):
  C038F2A9 FEF525C5 08091761 C55C457F
Раунд 08: X1=C55C457F X2=1813AAE4 X3=FEF525C5 X4=08091761
Раунд 07: X1=08091761 X2=BDE36703 X3=1813AAE4 X4=FEF525C5
Раунд 06: X1=FEF525C5 X2=0DE439DD X3=BDE36703 X4=1813AAE4
Раунд 05: X1=1813AAE4 X2=463C93F6 X3=0DE439DD X4=BDE36703
Раунд 04: X1=BDE36703 X2=D0A1D0B5 X3=463C93F6 X4=0DE439DD
Раунд 03: X1=0DE439DD X2=B5D0B9D1 X3=D0A1D0B5 X4=463C93F6
Раунд 02: X1=463C93F6 X2=20D0A4D0 X3=B5D0B9D1 X4=D0A1D0B5
Раунд 01: X1=D0A1D0B5 X2=D182D18C X3=20D0A4D0 X4=B5D0B9D1

========================================================================
РАСШИФРОВАННЫЙ ТЕКСТ
========================================================================
Сеть Фейстеля, 4 ветви, 8 раундов.
Лабораторная работа №3, вариант 1.

========================================================================
СРАВНЕНИЕ
========================================================================
Совпадение: да
```

---

## 9. Анализ результатов

Сеть Фейстеля сохраняет обратимость независимо от того, обратима ли функция F.  
Изменение параметров (ключ, число раундов, тип F) приводит к перестройке криптограммы.  
Использование 4 ветвей удобно для 128-битного блока и позволяет работать с 32-битными словами.

---

## 10. Выводы

1. Реализована сеть Фейстеля с 4 ветвями для 128-битного блока.  
2. Подтверждена корректность шифрования и дешифрования.  
3. Обеспечена возможность менять число раундов и функцию F.  
4. Выполнена подробная, минималистичная демонстрация работы алгоритма.
