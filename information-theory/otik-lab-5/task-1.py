#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RLE (табл. Л5.1, вариант 2) — кодер/декодер + автодемо для PyCharm.

Вариант (N=8) => ((N-1)%3)+1 = 2:
  - используется префикс-байт p (маркер команд);
  - бег одинаковых символов c!=p, L>=4 кодируется как: (p:8, (L-3):8, c:8)
  - бег p...p длиной L>=2           как: (p:8, (L-1):8, p:8)
  - одиночный символ p (L=1)       как: (p:8, 0:8)
  - все остальные одиночные/короткие символы (c!=p) выводятся «как есть».

Формат контейнера (по умолчанию):
  MAGIC[4]='RLE2' | VER[1]=0x01 | FLAGS[1] | P[1] | ORIG_SIZE[8] | PAYLOAD
  FLAGS бит0=1 => поле ORIG_SIZE (uint64 LE) присутствует.

Как пользоваться:
  1) Просто запустите файл БЕЗ аргументов (PyCharm ▶️) — он создаст тесты и
     сам прогонит кодер/декодер с отчётом.
  2) Либо используйте CLI:
     - encode: python rle_var2.py encode <in> <out> [--prefix auto|0x..|N] [--no-header] [-v]
     - decode: python rle_var2.py decode <in> <out> [--raw --prefix 0x..] [-v]
"""

from __future__ import annotations
import argparse
import os
import struct
from collections import Counter
from pathlib import Path
import random
import sys
import shutil
from typing import Tuple

# ---------- Константы формата ----------
MAGIC = b"RLE2"
VER = 0x01
FLAG_ORIGSZ = 0x01

# ---------- Утилиты ОС/путей ----------
ROOT = Path(__file__).resolve().parent
TEST_DIR = ROOT / "rle_tests"
OUT_DIR = ROOT / "out"
MARKER = ROOT / ".rle_first_run_done"

# ---------- Логика выбора префикса ----------
def pick_prefix_byte_auto(data: bytes) -> int:
    """Автовыбор префикса p: берём наименее частый байт (при равенстве — меньший)."""
    if not data:
        return 0
    cnt = Counter(data)
    least = min(range(256), key=lambda b: (cnt.get(b, 0), b))
    return least

# ---------- Кодирование ----------
def encode_payload(data: bytes, p: int) -> bytes:
    """Кодирование согласно правилам варианта 2 (бинарный PAYLOAD)."""
    out = bytearray()
    i, n = 0, len(data)

    while i < n:
        b = data[i]

        # 1) Беги из префикса p (L>=1, но кодирование зависит от L)
        if b == p:
            j = i
            # верхний предел L<=256 (т.к. L-1 кодируется как 1..255, отдельный случай L=1)
            while j < n and data[j] == p and (j - i) < 256:
                j += 1
            L = j - i
            if L == 1:
                # одиночный p -> (p, 0)
                out.extend((p, 0))
            else:
                # L>=2 -> (p, L-1, p)
                out.extend((p, (L - 1) & 0xFF, p))
            i = j
            continue

        # 2) Беги одинаковых символов c!=p (L>=1)
        j = i
        while j < n and data[j] == b and data[j] != p and (j - i) < 258:
            j += 1
        L = j - i

        if L >= 4:
            # длинный бег -> (p, L-3, c)
            out.extend((p, (L - 3) & 0xFF, b))
            i = j
        else:
            # короткие участки -> литералы
            out.append(b)
            i += 1

    return bytes(out)

# ---------- Декодирование ----------
def decode_payload(payload: bytes, p: int) -> bytes:
    """Декодирование PAYLOAD по тем же правилам."""
    out = bytearray()
    i, n = 0, len(payload)

    while i < n:
        b = payload[i]

        if b != p:
            out.append(b)
            i += 1
            continue

        if i + 1 >= n:
            raise ValueError("Некорректный поток: после префикса отсутствует поле длины.")

        length_byte = payload[i + 1]

        if length_byte == 0:
            # (p,0) -> одиночный p
            out.append(p)
            i += 2
            continue

        if i + 2 >= n:
            raise ValueError("Некорректный поток: после (p,len) отсутствует байт символа.")

        sym = payload[i + 2]

        if sym == p:
            # (p, L-1, p) -> L повторов p, L∈[2..256]
            L = 1 + length_byte
            out.extend([p] * L)
        else:
            # (p, L-3, c) -> L повторов c, L∈[4..258]
            L = 3 + length_byte
            out.extend([sym] * L)

        i += 3

    return bytes(out)



# ---------- Контейнер ----------
def write_container(path: Path, payload: bytes, p: int, orig_size: int, use_header: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        if use_header:
            flags = FLAG_ORIGSZ
            f.write(MAGIC)
            f.write(struct.pack("<B", VER))
            f.write(struct.pack("<B", flags))
            f.write(struct.pack("<B", p))
            f.write(struct.pack("<Q", orig_size))  # uint64 little-endian
        f.write(payload)

def read_container(path: Path, expect_header: bool) -> Tuple[bytes, int, int]:
    """Читает контейнер. Возвращает (payload, p, orig_size|-1)."""
    data = path.read_bytes()

    if not expect_header:
        raise ValueError("Для --raw декодирования нужен явный --prefix (или используйте контейнер).")

    if len(data) < 7:
        raise ValueError("Файл слишком короткий — нет заголовка.")
    if data[:4] != MAGIC:
        raise ValueError("Неверная сигнатура файла (ожидалось 'RLE2').")
    ver = data[4]
    if ver != VER:
        raise ValueError(f"Неподдерживаемая версия формата: {ver}")
    flags = data[5]
    p = data[6]
    off = 7
    orig_size = -1
    if flags & FLAG_ORIGSZ:
        if len(data) < off + 8:
            raise ValueError("Повреждённый заголовок: нет ORIG_SIZE.")
        orig_size = struct.unpack("<Q", data[off:off+8])[0]
        off += 8

    payload = data[off:]
    return payload, p, orig_size

# ---------- CLI-команды ----------
def human_ratio(out_size: int, in_size: int) -> str:
    if in_size == 0:
        return "n/a"
    ratio = out_size / in_size
    pct = (1.0 - ratio) * 100.0
    sign = "+" if pct >= 0 else ""
    return f"{ratio:.3f}  ({sign}{pct:.1f}% {'меньше' if pct>=0 else 'больше'})"

def cmd_encode(args):
    raw = Path(args.input).read_bytes()

    # выбор p
    if args.prefix.lower() == "auto":
        p = pick_prefix_byte_auto(raw)
        auto_chosen = True
    else:
        p = int(args.prefix, 0) & 0xFF
        auto_chosen = False

    payload = encode_payload(raw, p)
    write_container(Path(args.output), payload, p, len(raw), use_header=not args.no_header)

    if args.verbose:
        out_sz = (0 if args.no_header else (4+1+1+1+8)) + len(payload)
        print("== RLE v2: кодирование завершено ==")
        print(f"Вход:    {args.input}  ({len(raw)} байт)")
        print(f"Выход:   {args.output} ({out_sz} байт)")
        print(f"Префикс: 0x{p:02X} ({p})  [{'auto' if auto_chosen else 'fixed'}]")
        print(f"Payload: {len(payload)} байт; Оверхед заголовка: {0 if args.no_header else (4+1+1+1+8)} байт")
        print(f"Коэффициент сжатия: {human_ratio(out_sz, len(raw))}")
        print("Пределы длин бегов:")
        print("  - для c!=p: L ∈ [4..258]   -> (p, L-3, c)")
        print("  - для p...p: L ∈ [2..256] -> (p, L-1, p)")
        print("  - одиночный p: L = 1      -> (p, 0)")

def cmd_decode(args):
    if args.raw:
        if args.prefix is None:
            raise SystemExit("Для --raw декодирования укажите --prefix (например, --prefix 0x00).")
        p = int(args.prefix, 0) & 0xFF
        payload = Path(args.input).read_bytes()
        data = decode_payload(payload, p)
        Path(args.output).write_bytes(data)
        if args.verbose:
            print("== RLE v2: декодирование RAW-записи завершено ==")
            print(f"Вход (payload): {args.input} ({len(payload)} байт), префикс p=0x{p:02X}")
            print(f"Выход (данные): {args.output} ({len(data)} байт)")
        return

    payload, p, orig_size = read_container(Path(args.input), expect_header=True)
    data = decode_payload(payload, p)
    Path(args.output).write_bytes(data)



    if args.verbose:
        in_sz = os.path.getsize(args.input)
        print("== RLE v2: декодирование завершено ==")
        print(f"Вход (контейнер): {args.input} ({in_sz} байт)")
        print(f"  ├── префикс p: 0x{p:02X} ({p})")
        if orig_size >= 0:
            print(f"  ├── заявленный исходный размер: {orig_size} байт")
        print(f"  └── payload: {len(payload)} байт")
        print(f"Выход (данные):  {args.output} ({len(data)} байт)")
        if orig_size >= 0:
            print("Согласованность размеров:",
                  "OK" if orig_size == len(data) else f"НЕСОВПАДЕНИЕ (ожидалось {orig_size})")

def build_cli():
    p = argparse.ArgumentParser(
        description="RLE (табл. Л5.1, вариант 2) — кодер/декодер с контейнером 'RLE2'. "
                    "Без аргументов запускает демонстрацию с автогенерацией тестов."
    )
    sub = p.add_subparsers(dest="cmd")

    # encode
    pe = sub.add_parser("encode", help="закодировать файл")
    pe.add_argument("input", help="входной файл (данные)")
    pe.add_argument("output", help="выходной файл (контейнер или RAW)")
    pe.add_argument("--prefix", default="auto",
                    help="префикс-байт p: 'auto' (по умолчанию) или число (напр., 0x00, 255)")
    pe.add_argument("--no-header", action="store_true",
                    help="писать чистый поток без контейнера (RAW)")
    pe.add_argument("-v", "--verbose", action="store_true", help="подробный вывод")
    pe.set_defaults(func=cmd_encode)

    # decode
    pd = sub.add_parser("decode", help="декодировать файл")
    pd.add_argument("input", help="входной файл (контейнер RLE2 или RAW)")
    pd.add_argument("output", help="выходной файл (данные)")
    pd.add_argument("--raw", action="store_true",
                    help="читать вход как RAW-поток (без заголовка)")
    pd.add_argument("--prefix", help="префикс-байт p для --raw (например, 0x00)")
    pd.add_argument("-v", "--verbose", action="store_true", help="подробный вывод")
    pd.set_defaults(func=cmd_decode)

    return p

# ---------- Генерация тестов (создаётся только при первом запуске) ----------
def create_test_files():
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    def w(name: str, b: bytes):
        (TEST_DIR / name).write_bytes(b)

    # 1) Длинный бег c!=p (классика RLE)
    w("t1_100xA.bin", b"A" * 100)

    # 2) Бег из самого префикса p=0x00 (L>=2) + одиночный p
    w("t2_50x00_plus_single00.bin", b"\x00" * 50 + b"\x00")

    # 3) Смешанный: короткие и длинные беги, вкраплённые p
    w("t3_mixed.bin", b"AAAABBB" + b"\x00\x00Z\x00" + b"ABC" + b"\x00" + b"XXXXXXXX" + b"YY")

    # 4) Границы длин:
    #   - c!=p: L=4 (мин.) и L=258 (макс.)
    #   - p...p: L=2 (мин.) и L=256 (макс.)
    w("t4_edges.bin", b"X"*4 + b"Y"*258 + b"\x00"*2 + b"\x00"*256)

    # 5) «Плохой» для RLE — случайные байты
    random.seed(7)
    w("t5_random_4k.bin", bytes(random.getrandbits(8) for _ in range(4096)))

    # 6) Маленький без повторов
    w("t6_small_no_runs.bin", b"abcdef\x00ghij\x00klm")

# ---------- Автодемо: кодер -> декодер -> проверка ----------
def compare_files(a: Path, b: Path) -> bool:
    ba = a.read_bytes()
    bb = b.read_bytes()
    return ba == bb

def autodemo():
    print("=== RLE v2 (Л5.№1) — автодемонстрация ===")

    # 1) Если первый запуск — создаём тестовые файлы
    if not MARKER.exists():
        print("[INIT] Похоже, это первый запуск. Создаю тестовые файлы…")
        create_test_files()
        MARKER.write_text("ok")
    else:
        # убедимся, что тесты есть (могли быть удалены)
        if not TEST_DIR.exists() or not any(TEST_DIR.iterdir()):
            print("[INIT] Маркер есть, но папка тестов пуста — пересоздаю…")
            create_test_files()

    # 2) Готовим каталог вывода
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 3) Пробегаемся по всем тестам
    tests = sorted(p for p in TEST_DIR.glob("*.bin"))
    if not tests:
        print("[WARN] Тесты не найдены.")
        return



    ok = 0
    total = len(tests)
    print(f"[RUN] Найдено тестов: {total}")
    for t in tests:
        out_container = OUT_DIR / (t.stem + ".rle2")
        out_restored  = OUT_DIR / (t.stem + ".dec")

        # читаем исходник
        raw = t.read_bytes()
        # выбираем p автоматически
        p = pick_prefix_byte_auto(raw)
        # кодируем
        payload = encode_payload(raw, p)
        write_container(out_container, payload, p, len(raw), use_header=True)
        # декодируем
        payload2, p2, _orig = read_container(out_container, expect_header=True)
        data = decode_payload(payload2, p2)
        out_restored.write_bytes(data)

        same = (raw == data)
        if same:
            ok += 1

        # отчёт по тесту
        in_sz = len(raw)
        out_sz = (4+1+1+1+8) + len(payload)  # контейнерный размер
        ratio = human_ratio(out_sz, in_sz)
        print(f"  • {t.name:30s}  p=0x{p:02X}  "
              f"in={in_sz:6d}  out={out_sz:6d}  ratio={ratio}  "
              f"check={'OK' if same else 'FAIL'}")

    print(f"[DONE] Совпали: {ok}/{total} тестов.")
    print(f"Файлы вывода: {OUT_DIR}")
    print("Вы можете запустить encode/decode вручную через аргументы командной строки.\n")

# ---------- main ----------
def main():
    parser = build_cli()
    # Если аргументы отсутствуют — запускаем автодемонстрацию (для PyCharm Run)
    if len(sys.argv) == 1:
        autodemo()
        return

    args = parser.parse_args()
    if not hasattr(args, "func"):
        # если пользователь указал что-то вроде "-h" — argparse сам выведет помощь и выйдет
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
