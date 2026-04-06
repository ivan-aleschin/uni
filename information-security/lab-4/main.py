"""
Лабораторная работа №4 — Изучение алгоритмов RSA
Цель: шифрование и дешифрование данных в криптосистеме RSA
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует (gcd != 1).")
    return x % m


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


@dataclass
class RSAParams:
    p: int = 17
    q: int = 19
    e: int = 5


class RSA:
    def __init__(self, params: RSAParams) -> None:
        self.p = params.p
        self.q = params.q
        self.e = params.e

        if not is_prime(self.p) or not is_prime(self.q):
            raise ValueError("p и q должны быть простыми числами.")
        if self.p == self.q:
            raise ValueError("p и q должны быть различными.")

        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        if gcd(self.e, self.phi) != 1:
            raise ValueError("e не взаимно просто с φ(n).")

        self.d = modinv(self.e, self.phi)

        if self.n <= 255:
            raise ValueError("n должно быть больше 255 для байтового шифрования.")

    def encrypt_bytes(self, data: bytes) -> List[int]:
        return [pow(b, self.e, self.n) for b in data]

    def decrypt_bytes(self, data: List[int]) -> bytes:
        return bytes(pow(c, self.d, self.n) for c in data)


def banner(title: str) -> str:
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


def build_sample_text(min_len: int) -> str:
    parts = [
        "Лабораторная работа №4 посвящена RSA и принципам асимметричного шифрования. ",
        "Открытый ключ используется для шифрования, закрытый — для дешифрования. ",
        "Безопасность RSA опирается на трудность факторизации числа n = p·q. ",
        "В этом тексте представлены исходные данные и демонстрация работы алгоритма. ",
        "Текст составлен так, чтобы удовлетворять требованию минимальной длины. ",
        "Каждый блок сообщения кодируется как байт и шифруется по формуле c = m^e mod n. ",
        "Расшифрование выполняется по формуле m = c^d mod n. ",
        "Проверка взаимной простоты e и φ(n) необходима для существования обратного элемента d. ",
    ]
    text = "".join(parts)
    counter = 1
    while len(text) < min_len:
        text += f"Дополнение {counter}: приведены дополнительные пояснения к лабораторной работе. "
        counter += 1
    return text[:min_len]


def main() -> None:
    params = RSAParams(p=17, q=19, e=5)
    rsa = RSA(params)

    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, "input.txt")
    encrypted_file = os.path.join(base_dir, "encrypted.txt")
    decrypted_file = os.path.join(base_dir, "decrypted.txt")

    min_len = 2 * rsa.n  # требование 2n символов
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            plaintext = f.read()
    else:
        plaintext = ""

    if len(plaintext) < min_len:
        plaintext = build_sample_text(min_len)
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(plaintext)

    data = plaintext.encode("utf-8")

    print(banner("ПАРАМЕТРЫ RSA"))
    print(f"p = {rsa.p}")
    print(f"q = {rsa.q}")
    print(f"n = {rsa.n}")
    print(f"phi(n) = {rsa.phi}")
    print(f"e = {rsa.e}")
    print(f"d = {rsa.d}")
    print(f"gcd(e, phi) = {gcd(rsa.e, rsa.phi)}")

    print(banner("ИСХОДНЫЕ ДАННЫЕ"))
    print(f"Длина текста (символы): {len(plaintext)}")
    print(f"Длина текста (байты): {len(data)}")

    encrypted = rsa.encrypt_bytes(data)
    encrypted_str = " ".join(str(x) for x in encrypted)
    with open(encrypted_file, "w", encoding="utf-8") as f:
        f.write(encrypted_str)

    decrypted = rsa.decrypt_bytes(encrypted)
    decrypted_text = decrypted.decode("utf-8")
    with open(decrypted_file, "w", encoding="utf-8") as f:
        f.write(decrypted_text)

    print(banner("ДЕТАЛЬНАЯ ДЕМОНСТРАЦИЯ (ПЕРВЫЕ 10 БАЙТ)"))
    limit = min(10, len(data))
    for i in range(limit):
        m = data[i]
        c = encrypted[i]
        m_back = decrypted[i]
        print(f"{i:02d}: m=0x{m:02X} -> c={c} -> m'=0x{m_back:02X}")

    print(banner("КРИПТОГРАММА"))
    print(f"Всего чисел: {len(encrypted)}")
    print("Первые 10:", " ".join(map(str, encrypted[:10])))
    print("Последние 10:", " ".join(map(str, encrypted[-10:])))

    print(banner("СРАВНЕНИЕ"))
    print(f"Совпадение: {'да' if plaintext == decrypted_text else 'нет'}")


if __name__ == "__main__":
    main()
