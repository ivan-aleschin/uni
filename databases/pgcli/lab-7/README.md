# Лабораторная работа 7

## Задание
**Реализовать программу для работы с БД, использующую ранее подготовленные процедуры** (из Лабораторной работы 5).

---

---

## Теория: Приложения для работы с PostgreSQL

### psycopg2 — адаптер PostgreSQL для Python
```python
import psycopg2
conn = psycopg2.connect(host='localhost', dbname='demo', user='postgres')
cur = conn.cursor()

# Выполнить запрос с параметрами (защита от SQL-инъекций!)
cur.execute("SELECT * FROM flights WHERE flight_id = %s", (flight_id,))
rows = cur.fetchall()

conn.commit()   # подтвердить транзакцию
conn.rollback() # или откатить при ошибке
conn.close()
```

### Почему параметризованные запросы?
**НИКОГДА** не делать так:
```python
# ❌ SQL-инъекция!
cur.execute(f"SELECT * FROM flights WHERE route_no = '{user_input}'")
```
Если `user_input = "'; DROP TABLE flights;--"` — таблица удалится.

**Правильно** — через `%s` плейсхолдеры:
```python
# ✅ psycopg2 экранирует значение
cur.execute("SELECT * FROM flights WHERE route_no = %s", (user_input,))
```

### DictCursor — доступ по имени столбца
```python
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("SELECT flight_id, route_no FROM flights LIMIT 1")
row = cur.fetchone()
print(row['flight_id'])  # по имени, не по индексу
```

### Управление транзакциями
- psycopg2 **автоматически** открывает транзакцию при первом запросе.
- Без `commit()` изменения не сохранятся (при закрытии соединения — откат).
- Используй `try/except` с `rollback()` для безопасной обработки ошибок.

### Вызов хранимой функции из Python
```python
cur.execute("SELECT book_ticket(%s, %s, %s, %s, %s)",
            (passenger_id, passenger_name, flight_id, fare_conditions, price))
book_ref = cur.fetchone()[0]
conn.commit()
```

---

## Программа: `app.py`

Интерактивное CLI-приложение на Python, подключающееся к базе `demo` через библиотеку `psycopg2`.

### Возможности
| Пункт меню | Действие | Используемая процедура/запрос |
|---|---|---|
| 1 | Показать 20 ближайших рейсов со свободными местами | `check_free_seats()` |
| 2 | Забронировать билет (интерактивный ввод) | `book_ticket()` |
| 3 | Найти бронирование по коду | JOIN bookings/tickets/segments |
| 0 | Выход | — |

### Обработка ошибок
Все исключения от PostgreSQL (ошибка рейса, нет мест, неверный класс) перехватываются и выводятся на русском языке через `e.pgerror`.

---

## Запуск (NixOS)

Зависимость `psycopg2` объявлена в `databases/pgcli/pyproject.toml` и предоставляется через `flake.nix` (через `python3.withPackages`). Запускать из `nix develop`:

```bash
# 1. Войти в devShell (из корня репозитория)
nix develop

# 2. Запустить приложение (находясь в папке lab-7)
python3 app.py
```

> **Почему не `uv install` / `pip install`?**
> На NixOS бинарные колёса (`psycopg2-binary`) не работают: они бандлят `libpq.so` под стандартные пути `/lib/x86_64-linux-gnu/`, которых в Nix нет. Поэтому `psycopg2` разрешается через Nix (`python3.withPackages`), а `uv` используется для чистых Python-проектов без C-расширений.

> ⚠️ Предварительно должны быть применены процедуры из `lab-5/01_procedure.sql`.

---

## Пример работы

```
╔═══════════════════════════════════════════╗
║   Система бронирования авиабилетов        ║
║   БД: demo (PostgresPro)                  ║
╚═══════════════════════════════════════════╝
  Подключено к: PostgresPro 2025-09-01 (91 days)

  1 — Доступные рейсы
  2 — Забронировать билет
  3 — Найти бронирование
  0 — Выход

Действие: 2

[показывает список рейсов]

ID рейса: 12136
ID документа: RU 1234567890123
Имя: Ivan Petrov
Класс [1/2/3]: 1
Цена (Economy), руб.: 4500

  ✓ Бронирование создано!
    Номер бронирования : G0NWW5
    Пассажир           : Ivan Petrov
    Рейс / Класс / Цена: 12136 / Economy / 4500.00 руб.
```

---

## Технические детали

- **Библиотека**: `psycopg2` (PostgreSQL adapter for Python)
- **Python**: предоставляется `flake.nix` через `python3.withPackages [psycopg2]`
- **Параметризованные запросы**: все SQL-запросы используют `%s`-плейсхолдеры, что защищает от SQL-инъекций
- **Транзакции**: `psycopg2` открывает транзакцию автоматически; при ошибке вызывается `conn.rollback()`
- **DictCursor**: результаты доступны по имени колонки (`row['flight_id']`), а не по индексу
