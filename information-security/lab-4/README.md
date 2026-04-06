# Отчет по лабораторной работе № 4

**Тема:** ИЗУЧЕНИЕ АЛГОРИТМОВ RSA  
**Дисциплина:** Защита информации  

---

## 1. Задание

1. Разработать программу, осуществляющую шифрование и дешифрование алгоритмом RSA.  
2. Исходное сообщение M должно состоять не менее чем из 2n символов.  
3. Зашифрованный текст оформить в виде отдельного файла.  
4. В программе предусмотреть проверку, являются ли два числа взаимно простыми.  
5. Оформить результаты в виде отчета.  
6. Содержание отчета:  
   - описание используемого метода;  
   - описание исходных данных;  
   - алгоритм работы программы;  
   - текст программы;  
   - результаты работы программы;  
   - анализ результатов;  
   - выводы.

---

## 2. Теория

### 2.1. Криптосистемы с открытым ключом

В асимметричных криптосистемах используются два ключа:  
- **открытый** (публикуется и применяется для шифрования),  
- **закрытый** (хранится в секрете и применяется для дешифрования).  

Безопасность основана на **однонаправленных функциях**: значение f(x) вычисляется легко, а обратная операция — вычислительно сложна.

### 2.2. RSA

Алгоритм RSA строится так:

1. Выбираются два простых числа p и q.  
2. Вычисляется n = p⋅q.  
3. Вычисляется φ(n) = (p−1)(q−1).  
4. Выбирается e, взаимно простое с φ(n).  
5. Вычисляется d как обратное к e по модулю φ(n):  
   (e⋅d) mod φ(n) = 1.  

Открытый ключ: (e, n)  
Закрытый ключ: (d, p, q)

Шифрование:  
C = M^e mod n  

Дешифрование:  
M = C^d mod n

---

## 3. Исходные данные

- Примерные параметры (учебные, малые):  
  - p = 17  
  - q = 19  
  - n = 323  
  - φ(n) = 288  
  - e = 5  
  - d = 173  
- Требование 2n символов выполнено:  
  - 2n = 646  
  - сообщение длиной 646 символов  

Файлы:  
- `input.txt` — исходный текст  
- `encrypted.txt` — криптограмма (числа)  
- `decrypted.txt` — восстановленный текст  

---

## 4. Алгоритм работы программы

1. Проверка, что p и q — простые.  
2. Расчет n и φ(n).  
3. Проверка взаимной простоты e и φ(n) (через gcd).  
4. Вычисление d (расширенный алгоритм Евклида).  
5. Кодирование текста в байты (UTF-8).  
6. Шифрование каждого байта: c = b^e mod n.  
7. Запись криптограммы в `encrypted.txt`.  
8. Дешифрование: b = c^d mod n.  
9. Запись результата в `decrypted.txt`.  
10. Сравнение с исходным текстом.

---

## 5. Полный текст программы

```uni/information-security/lab-4/main.py#L1-L200
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
```

---

## 6. Демонстрация (минималистичная и подробная)

Программа выводит:

- параметры RSA и проверку взаимной простоты,  
- длину текста,  
- пошаговую демонстрацию первых 10 байт,  
- статистику криптограммы (количество, первые/последние значения),  
- сравнение результатов.

---

## 7. Пример запуска (nix-shell)

```uni/information-security/lab-4/README.md#L300-L320
$ cd information-security/lab-4
$ nix-shell -p python3 --run "python3 main.py"
```

---

## 8. Результаты работы программы

Пример фактического вывода:

```uni/information-security/lab-4/README.md#L330-L420
========================================================================
ПАРАМЕТРЫ RSA
========================================================================
p = 17
q = 19
n = 323
phi(n) = 288
e = 5
d = 173
gcd(e, phi) = 1

========================================================================
ИСХОДНЫЕ ДАННЫЕ
========================================================================
Длина текста (символы): 646
Длина текста (байты): 1159

========================================================================
ДЕТАЛЬНАЯ ДЕМОНСТРАЦИЯ (ПЕРВЫЕ 10 БАЙТ)
========================================================================
00: m=0xD0 -> c=208 -> m'=0xD0
01: m=0x9B -> c=15 -> m'=0x9B
02: m=0xD0 -> c=208 -> m'=0xD0
03: m=0xB0 -> c=313 -> m'=0xB0
04: m=0xD0 -> c=208 -> m'=0xD0
05: m=0xB1 -> c=62 -> m'=0xB1
06: m=0xD0 -> c=208 -> m'=0xD0
07: m=0xBE -> c=209 -> m'=0xBE
08: m=0xD1 -> c=133 -> m'=0xD1
09: m=0x80 -> c=314 -> m'=0x80

========================================================================
КРИПТОГРАММА
========================================================================
Всего чисел: 1159
Первые 10: 208 15 208 313 208 62 208 209 133 314
Последние 10: 209 133 314 208 151 208 209 208 257 223

========================================================================
СРАВНЕНИЕ
========================================================================
Совпадение: да
```

---

## 9. Анализ результатов

Алгоритм RSA корректно шифрует и дешифрует данные при совпадении ключей.  
Проверка взаимной простоты гарантирует существование обратного элемента d.  
Модульное возведение в степень выполняется эффективно с помощью `pow(a, e, n)`.  

---

## 10. Выводы

1. Реализован алгоритм RSA с генерацией параметров и проверкой gcd.  
2. Выполнены шифрование и дешифрование текста.  
3. Получена криптограмма и записана в отдельный файл.  
4. Демонстрация выполнена подробно и без лишней символики.
