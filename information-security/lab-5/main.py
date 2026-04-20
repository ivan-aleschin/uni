#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №5 — Создание электронной подписи в документе (образец)
Реализация упрощённой схемы ЭЦП по описанию (аналог ГОСТ Р34.10-94 / DSA-like),
с хеш-функцией по варианту 1:
    "Количество 1 в битовом представлении символов исходного текста"

Файл:
    uni/information-security/lab-5/main.py

Что делает:
- выбирает параметры системы (p, q, a) совместимые по требованию q | (p-1)
- генерирует закрытый ключ x и открытый ключ y = a^x mod p
- вычисляет простую хеш-функцию H(m): количество единиц в битовом представлении
- формирует подпись (r, s) по алгоритму, указанному в задании
- проверяет подпись; демонстрирует, что при изменении сообщения подпись становится недействительной

Запуск:
    python3 main.py

Результат:
- печать параметров, ключей, дайджеста, подписи и результатов проверки
- файлы (в каталоге скрипта):
    - input.txt      — входное сообщение (создаётся, если отсутствует)
    - signature.txt  — подпись: два числа r s
"""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from typing import Tuple

# --------------------------
# Утилиты / баннер
# --------------------------


def banner(title: str) -> str:
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


# --------------------------
# Хеш-функция (вариант 1)
# --------------------------


def hash_count_ones(message: bytes) -> int:
    """
    Хеш-функция по варианту:
    количество единичных битов во всём байтовом представлении сообщения.
    Возвращает неограниченное по размеру целое.
    """
    total = 0
    for b in message:
        # bin(b) -> '0b101010' ; count '1'
        total += bin(b).count("1")
    return total


# --------------------------
# Параметры ЭЦП, генерация ключей
# --------------------------


@dataclass
class ECPParams:
    p: int
    q: int
    a: int


@dataclass
class KeyPair:
    x: int  # secret (private)
    y: int  # public


def find_a_for_subgroup(p: int, q: int) -> int:
    """
    Найти число a (1 < a < p-1) такое, что a^q mod p == 1 и a != 1.
    (т.е. элемент из подгруппы порядка делителя q)
    """
    for candidate in range(2, p - 1):
        if pow(candidate, q, p) == 1:
            return candidate
    raise RuntimeError("Не удалось найти подходящий параметр a для заданных p и q")


def default_params() -> ECPParams:
    """
    Возвращает пример параметров системы (некриптографически сильных,
    подобранных для демонстрационных целей).
    p - простое, q - простое и q | (p-1)
    """
    # Пример небольших параметров, где q | (p-1):
    # p = 467, p-1 = 466, q = 233 (466 = 2 * 233)
    p = 467
    q = 233
    a = find_a_for_subgroup(p, q)
    return ECPParams(p=p, q=q, a=a)


def generate_keypair(params: ECPParams) -> KeyPair:
    """
    Генерирует секретный ключ x и открытый ключ y = a^x mod p.
    x в диапазоне 1 < x < q
    """
    q = params.q
    # secrets for cryptographic-like randomness
    x = secrets.randbelow(q - 1) + 1  # 1..q-1
    y = pow(params.a, x, params.p)
    return KeyPair(x=x, y=y)


# --------------------------
# Формирование подписи
# --------------------------


def sign_message(message: bytes, params: ECPParams, key: KeyPair) -> Tuple[int, int]:
    """
    Подписывает сообщение по алгоритму, описанному в задании:
    1) h = H(m); если h (mod p) == 0 -> h = 1
    2) выбрать случайный k в [1, q-1]
    3) r = a^k mod p ; r1 = r mod q ; если r1 == 0 -> повторить выбор k
    4) s = (x*r1 + k*h) mod q ; если s == 0 -> повторить (выбрать новый k)
    Возвращает (r1, s)
    """
    p, q, a = params.p, params.q, params.a
    x = key.x

    h_full = hash_count_ones(message)
    # по описанию: если h(m) (mod p) == 0, то h(m) присваивается значение 1
    if h_full % p == 0:
        h_full = 1

    # для вычислений модуля q лучше взять h mod q
    h_q = h_full % q
    if h_q == 0:
        # чтобы иметь обратимый элемент по модулю q (при проверке потребуется)
        h_q = 1

    while True:
        k = secrets.randbelow(q - 1) + 1  # 1..q-1
        r = pow(a, k, p)
        r1 = r % q
        if r1 == 0:
            continue
        s = (x * r1 + k * h_q) % q
        if s == 0:
            continue
        return r1, s


# --------------------------
# Проверка подписи
# --------------------------


def verify_signature(
    message: bytes, signature: Tuple[int, int], params: ECPParams, public_y: int
) -> bool:
    """
    Проверка подписи:
    1) проверить 0 < r1 < q и 0 < s < q
    2) h = H(m); если h (mod p) == 0 -> h = 1
    3) v = h^(q-2) (mod q)  -- обратный по модулю q
    4) z1 = s*v (mod q); z2 = (q - r1)*v (mod q)
    5) u = (a^z1 * y^z2 mod p) mod q
    6) подпись действительна, если u == r1
    """
    p, q, a = params.p, params.q, params.a
    r1, s = signature

    if not (0 < r1 < q and 0 < s < q):
        return False

    h_full = hash_count_ones(message)
    if h_full % p == 0:
        h_full = 1

    h_q = h_full % q
    if h_q == 0:
        # в случае, когда h ≡ 0 (mod q), обратного не будет; приведём к 1
        # (такой шаг использован и в генерации подписи для консистентности)
        h_q = 1

    # вычисляем v = inverse(h_q) mod q
    # используя малый q (простое), можем взять pow(h_q, q-2, q)
    try:
        v = pow(h_q, q - 2, q)
    except ValueError:
        # на практике pow не бросает для корректных аргументов; оставим обработку
        return False

    z1 = (s * v) % q
    z2 = ((q - r1) * v) % q

    u = (pow(a, z1, p) * pow(public_y, z2, p)) % p
    u_mod_q = u % q

    return u_mod_q == r1


# --------------------------
# Демонстрация сценария работы
# --------------------------


def main() -> None:
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, "input.txt")
    signature_file = os.path.join(base_dir, "signature.txt")

    # подготовим входной текст (если отсутствует)
    if not os.path.exists(input_file):
        sample = (
            "Тестовое сообщение для лабораторной работы №5. "
            "Проверка формирования и проверки электронной подписи.\n"
        )
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(sample)

    with open(input_file, "r", encoding="utf-8") as f:
        plaintext = f.read()

    message_bytes = plaintext.encode("utf-8")

    # Параметры системы и ключи
    params = default_params()
    keys = generate_keypair(params)

    print(banner("ПАРАМЕТРЫ СИСТЕМЫ ЭЦП"))
    print(f"p = {params.p}")
    print(f"q = {params.q}")
    print(f"a = {params.a}")

    print(banner("КЛЮЧИ"))
    print(f"Секретный ключ x = {keys.x}")
    print(f"Открытый ключ y = {keys.y}")

    # хеш (дайджест)
    h = hash_count_ones(message_bytes)
    print(banner("ХЭШ-ФУНКЦИЯ (вариант 1)"))
    print(f"Хеш (кол-во единиц в битах) H(m) = {h}")
    if h % params.p == 0:
        print(
            "H(m) ≡ 0 (mod p) -> при подписывании и проверке будет использовано значение 1"
        )

    # генерация подписи
    signature = sign_message(message_bytes, params, keys)
    r1, s = signature
    print(banner("ПОДПИСЬ"))
    print(f"r = {r1}")
    print(f"s = {s}")

    # сохранить подпись
    with open(signature_file, "w", encoding="utf-8") as f:
        f.write(f"{r1} {s}\n")

    # собрать и сохранить подписанное сообщение (JSON) — включает исходный текст, хеш и подпись
    signed = {
        "message": plaintext,
        "hash": h,
        "r": r1,
        "s": s,
        "params": {"p": params.p, "q": params.q, "a": params.a},
        "y": keys.y,
    }
    signed_file = os.path.join(base_dir, "signed_message.json")
    with open(signed_file, "w", encoding="utf-8") as f:
        json.dump(signed, f, ensure_ascii=False, indent=2)

    # вывести блок подписанного сообщения (аналогично lab-4: исходный -> подписанный -> проверка)
    print(banner("ИСХОДНЫЙ ТЕКСТ"))
    print(plaintext)
    print(banner("ПОДПИСАННОЕ СООБЩЕНИЕ (JSON)"))
    print(json.dumps(signed, ensure_ascii=False, indent=2))

    # проверка подписи (оригинальное сообщение)
    ok = verify_signature(message_bytes, signature, params, keys.y)
    print(banner("ПРОВЕРКА ПОДПИСИ (ОРИГИНАЛЬНОЕ СООБЩЕНИЕ)"))
    print(f"Подпись {'ДЕЙСТВИТЕЛЬНА' if ok else 'НЕДЕЙСТВИТЕЛЬНА'}")

    # изменим сообщение (имитация подмены) и проверим, что подпись не пройдёт
    tampered_text = plaintext + "\n1"
    tampered_bytes = tampered_text.encode("utf-8")
    ok2 = verify_signature(tampered_bytes, signature, params, keys.y)
    print(banner("ПРОВЕРКА ПОДПИСИ (ИЗМЕНЁННОЕ СООБЩЕНИЕ)"))
    print(
        f"Подпись {'ДЕЙСТВИТЕЛЬНА' if ok2 else 'НЕДЕЙСТВИТЕЛЬНА'} (ожидается: НЕДЕЙСТВИТЕЛЬНА)"
    )

    # вывод краткого резюме
    print(banner("РЕЗЮЛЬТАТЫ"))
    print(f"Файл с сообщением: {input_file}")
    print(f"Файл с подписью: {signature_file}")
    print(f"Проверка на оригинале: {'OK' if ok else 'FAIL'}")
    print(f"Проверка на изменённом: {'OK' if ok2 else 'FAIL'}")


if __name__ == "__main__":
    main()
