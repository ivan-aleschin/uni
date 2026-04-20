#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №6 — Парольная защита (вариант 1: выборка символов)

Реализована учебная схема "выборка символов" (selection-of-symbols).
При регистрации для каждого символа пароля сохраняется его
проверочный хеш (salt + username + позиция + символ).
При входе система случайно запрашивает несколько символов пароля
по номерам позиций (пример: 2-й, 5-й и т.д.) и сверяет полученные
символы с сохранёнными хешами.

Файлы, создаваемые и используемые в каталоге этой лабораторной:
 - users.json    — файл с информацией о зарегистрированных пользователях
                   (username, salt, length, char_hashes, last_login, locked_until)
 - input.txt     — (опционально) пример текста/инструкции

Запуск:
    python3 main.py

Программа поддерживает:
 - регистрацию пользователя
 - вход пользователя с выборкой символов
 - смену пароля (при успешном входе)
 - демонстрацию неудачной проверки и блокировки после N неудачных попыток
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import secrets
import time
from typing import Any, Dict, List, Tuple

# --------------------------
# Конфигурация
# --------------------------
DATA_FILE = "users.json"
MAX_ATTEMPTS = 3  # попыток ввода (сессий входа) до блокировки
BLOCK_SECONDS = 15  # время блокировки в секундах после превышения попыток
REQUESTED_SYMBOLS = (
    3  # сколько символов запрашивать при входе (если пароль короче, - меньше)
)
SALT_BYTES = 16  # количество байт для salt (hex-строка будет в 2x длины)

# --------------------------
# Вспомогательные функции
# --------------------------


def banner(title: str) -> str:
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


def load_users(path: str = DATA_FILE) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(data: Dict[str, Any], path: str = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_char_hash(salt: str, username: str, pos: int, ch: str) -> str:
    """
    Хеш для одного символа: sha256(salt + ':' + username + ':' + pos + ':' + ch)
    Используем UTF-8 для символов, чтобы поддерживать Unicode.
    """
    payload = f"{salt}:{username}:{pos}:".encode("utf-8") + ch.encode("utf-8")
    return sha256_hex(payload)


def generate_salt() -> str:
    return secrets.token_hex(SALT_BYTES)


# --------------------------
# Регистрация и хранение
# --------------------------


def register_user(users: Dict[str, Any]) -> None:
    print(banner("РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ"))
    while True:
        username = input("Введите имя пользователя (username): ").strip()
        if not username:
            print("Имя пользователя не может быть пустым.")
            continue
        if username in users:
            print("Пользователь с таким именем уже зарегистрирован.")
            return
        break

    # ввод пароля — дважды, без эхо
    while True:
        pwd1 = getpass.getpass("Введите пароль: ")
        pwd2 = getpass.getpass("Повторите пароль: ")
        if pwd1 != pwd2:
            print("Пароли не совпадают. Попробуйте ещё раз.")
            continue
        if len(pwd1) == 0:
            print("Пароль не может быть пустым.")
            continue
        break

    salt = generate_salt()
    length = len(pwd1)

    # сформируем список хешей по позициям (позиции нумеруем с 1)
    char_hashes: List[str] = []
    for i, ch in enumerate(pwd1, start=1):
        char_hashes.append(make_char_hash(salt, username, i, ch))

    users[username] = {
        "salt": salt,
        "length": length,
        "char_hashes": char_hashes,
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
    }
    save_users(users)
    print(
        f"Пользователь '{username}' зарегистрирован. Длина пароля: {length} символов."
    )
    print(
        "Внимание: в этой учебной реализации система хранит по одному хешу на каждый символ пароля."
    )


# --------------------------
# Проведение входа (selection-of-symbols)
# --------------------------


def choose_positions(length: int, count: int) -> List[int]:
    """
    Случайно выбирает 'count' различных позиций (1..length).
    Если length < count, возвращает все позиции.
    """
    if length <= 0:
        return []
    count = min(count, length)
    # используем secrets.sample-like approach
    positions = list(range(1, length + 1))
    # secrets.choice used repeatedly to build unique sample
    chosen: List[int] = []
    while len(chosen) < count:
        pick = secrets.choice(positions)
        if pick not in chosen:
            chosen.append(pick)
    chosen.sort()
    return chosen


def is_locked(user: Dict[str, Any]) -> Tuple[bool, float]:
    locked_until = user.get("locked_until")
    if not locked_until:
        return False, 0.0
    now = time.time()
    if now >= locked_until:
        # сброс блокировки
        user["locked_until"] = None
        user["failed_attempts"] = 0
        return False, 0.0
    return True, locked_until - now


def authenticate_user(users: Dict[str, Any]) -> None:
    print(banner("АВТОРИЗАЦИЯ (ВХОД) — ВЫБОРКА СИМВОЛОВ"))
    username = input("Введите имя пользователя: ").strip()
    if username not in users:
        print("Пользователь не найден.")
        return

    user = users[username]
    locked, remaining = is_locked(user)
    if locked:
        print(
            f"Учётная запись заблокирована. Повтор можно попытаться через {int(remaining)} сек."
        )
        return

    length: int = user["length"]
    char_hashes: List[str] = user["char_hashes"]
    salt: str = user["salt"]

    # на каждой сессии случайно выбираем позиции
    positions = choose_positions(length, REQUESTED_SYMBOLS)
    print(
        f"Система запросит символы пароля по следующим позициям (номера символов, начиная с 1): {positions}"
    )

    # запросим символы — используем getpass, чтобы не отображать на экране
    provided_ok = True
    for pos in positions:
        prompt = f"Введите символ на позиции {pos}: "
        # хоть пользователь вводит один символ, мы позволяем вводить несколько (в таком случае берем первый символ)
        entry = getpass.getpass(prompt)
        if entry == "":
            # пустой ввод считается неверным
            provided_ok = False
            print("Пустой ввод — неверный символ.")
            break
        ch = entry[0]  # первый символ, если введено больше
        expected_hash = char_hashes[pos - 1]
        given_hash = make_char_hash(salt, username, pos, ch)
        if given_hash != expected_hash:
            provided_ok = False
            print(f"Символ на позиции {pos} НЕ соответствует сохранённому значению.")
            break
        else:
            print(f"Символ на позиции {pos} — верный.")

    if provided_ok:
        print("Вход успешен. Добро пожаловать!")
        user["last_login"] = time.time()
        user["failed_attempts"] = 0
        user["locked_until"] = None
        save_users(users)
        # после успешного входа предложим сменить пароль
        post_login_menu(users, username)
    else:
        user["failed_attempts"] = user.get("failed_attempts", 0) + 1
        print(
            f"Неверные символы. Попыток неудачно: {user['failed_attempts']}/{MAX_ATTEMPTS}"
        )
        if user["failed_attempts"] >= MAX_ATTEMPTS:
            user["locked_until"] = time.time() + BLOCK_SECONDS
            print(
                f"Слишком много неудачных попыток. Учётная запись заблокирована на {BLOCK_SECONDS} сек."
            )
        save_users(users)


# --------------------------
# Смена пароля (изменение полного пароля)
# --------------------------


def change_password(users: Dict[str, Any], username: str) -> None:
    print(banner("СМЕНА ПАРОЛЯ"))
    user = users[username]
    # запрос текущего полного пароля (пришли сюда только после успешного входа, но на всякий случай проверим)
    confirm = getpass.getpass("Для подтверждения введите текущий пароль полностью: ")
    # проверим, что полный пароль корректен, по символам (как простая, не лучшая проверка)
    # проверим длину и все символы
    if len(confirm) != user["length"]:
        print("Неверный пароль (длина не совпадает). Отмена смены.")
        return
    # проверим все символы
    for i, ch in enumerate(confirm, start=1):
        if make_char_hash(user["salt"], username, i, ch) != user["char_hashes"][i - 1]:
            print("Неверный пароль (символы не совпадают). Отмена смены.")
            return

    while True:
        new1 = getpass.getpass("Введите новый пароль: ")
        new2 = getpass.getpass("Повторите новый пароль: ")
        if new1 != new2:
            print("Пароли не совпадают. Попробуйте ещё раз.")
            continue
        if len(new1) == 0:
            print("Пароль не может быть пустым.")
            continue
        break

    # обновим salt и хеши
    new_salt = generate_salt()
    new_hashes: List[str] = []
    for i, ch in enumerate(new1, start=1):
        new_hashes.append(make_char_hash(new_salt, username, i, ch))

    user["salt"] = new_salt
    user["length"] = len(new1)
    user["char_hashes"] = new_hashes
    user["failed_attempts"] = 0
    user["locked_until"] = None
    save_users(users)
    print("Пароль успешно изменён.")


# --------------------------
# Меню после успешного входа
# --------------------------


def post_login_menu(users: Dict[str, Any], username: str) -> None:
    while True:
        print(banner("МЕНЮ ПОЛЬЗОВАТЕЛЯ"))
        print("1) Сменить пароль")
        print("2) Просмотреть информацию о последнем входе")
        print("0) Выйти")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            change_password(users, username)
        elif choice == "2":
            last = users[username].get("last_login")
            if last:
                print("Последний успешный вход:", time.ctime(last))
            else:
                print("Информация о предыдущем входе отсутствует.")
        elif choice == "0":
            print("Выход из сеанса пользователя.")
            break
        else:
            print("Неверный выбор.")


# --------------------------
# Основное меню программы
# --------------------------


def main() -> None:
    print(banner("ЛАБОРАТОРНАЯ РАБОТА №6 — ПАРОЛЬНАЯ ЗАЩИТА (ВЫБОРКА СИМВОЛОВ)"))
    users = load_users()

    while True:
        print(banner("ОСНОВНОЕ МЕНЮ"))
        print("1) Регистрация нового пользователя")
        print("2) Вход (selection-of-symbols)")
        print("3) Показать список пользователей (только имена)")
        print("0) Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            register_user(users)
            users = load_users()  # перезагрузим на случай внешних изменений
        elif choice == "2":
            users = load_users()
            authenticate_user(users)
            users = load_users()
        elif choice == "3":
            if users:
                print("Зарегистрированные пользователи:")
                for name in users.keys():
                    info = users[name]
                    print(
                        f" - {name} (len={info.get('length')}, locked={info.get('locked_until') is not None})"
                    )
            else:
                print("Пользователей нет.")
        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Неверный выбор. Попробуйте ещё раз.")


if __name__ == "__main__":
    main()
