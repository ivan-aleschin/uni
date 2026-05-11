# Лабораторная работа 8

## Задание
**Доработка структуры, запросов, процедур и программного обеспечения.**

---

---

## Теория: Триггеры и целостность данных

### Триггеры в PostgreSQL
Триггер — автоматически вызываемый код при `INSERT`, `UPDATE`, `DELETE` или `TRUNCATE`.

```sql
-- 1. Создать функцию-триггер (RETURNS TRIGGER, не обычный тип)
CREATE OR REPLACE FUNCTION my_trigger_fn()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- NEW — новая строка (для INSERT/UPDATE)
    -- OLD — старая строка (для UPDATE/DELETE)
    IF NEW.col < 0 THEN
        RAISE EXCEPTION 'Отрицательное значение запрещено';
    END IF;
    RETURN NEW;  -- передать строку дальше (или NULL чтобы отменить)
END;
$$;

-- 2. Прикрепить к таблице
CREATE TRIGGER my_trigger
    BEFORE INSERT ON my_table
    FOR EACH ROW
    EXECUTE FUNCTION my_trigger_fn();
```

### Типы триггеров
| Параметр | Варианты | Когда использовать |
|---|---|---|
| Момент | `BEFORE` / `AFTER` | `BEFORE` — для валидации и изменения NEW; `AFTER` — для каскадных действий |
| Событие | `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` | Выбирается по операции |
| Гранулярность | `FOR EACH ROW` / `FOR EACH STATEMENT` | ROW — на каждую строку; STATEMENT — раз на всю команду |

### Зачем триггеры, если есть CHECK в процедуре?
- `book_ticket()` проверяет места, но кто-то может вставить сегмент **напрямую** через `INSERT`.
- Триггер `BEFORE INSERT ON segments` защищает данные **на уровне СУБД**, независимо от приложения.
- Принцип **defense in depth**: приложение + БД оба проверяют инварианты.

### Каскадное удаление vs ручное
```sql
-- Вариант 1: ON DELETE CASCADE (автоматически)
REFERENCES parent(id) ON DELETE CASCADE

-- Вариант 2: ручное удаление в функции (больше контроля)
DELETE FROM child WHERE parent_id = v_id;
DELETE FROM parent WHERE id = v_id;
```
В `cancel_booking` используем **ручной** вариант, чтобы сначала проверить статус рейса.

---

## Что добавлено и улучшено

### 1. Новая процедура: `cancel_booking(book_ref TEXT)`
Отмена бронирования с проверкой статуса рейса:
- Бросает исключение, если бронирование не найдено.
- Бросает исключение, если рейс уже в пути (статус не `Scheduled`/`On Time`).
- Атомарно удаляет: `segments` → `tickets` → `bookings`.

### 2. Новая функция: `get_flight_info(flight_id INT)`
Возвращает полную информацию о рейсе одним вызовом:
- Названия городов на русском языке.
- Время вылета в местном часовом поясе аэропорта.
- `total_seats`, `sold_seats`, `free_seats`.

Используется в Python-приложении вместо сырого JOIN-запроса — приложение теперь не содержит бизнес-логики в Python-коде.

### 3. Триггер: `trg_segments_overbooking`
Защита целостности данных на уровне СУБД:
```sql
BEFORE INSERT ON segments → trg_check_overbooking()
```
- Вызывает `check_free_seats(NEW.flight_id)` перед каждой вставкой.
- Если мест нет — `RAISE EXCEPTION`, транзакция откатывается.
- Обеспечивает защиту от переполнения **даже при прямых `INSERT`**, минуя `book_ticket()`.

### 4. Улучшенное Python-приложение (`app.py`)
По сравнению с `lab-7/app.py` добавлено:
- Пункт меню **2 — Детали рейса**: вызывает `get_flight_info()`, показывает полную информацию.
- Пункт меню **5 — Отменить бронирование**: вызывает `cancel_booking()` с подтверждением.
- Города на русском языке при выводе списка рейсов.
- Улучшенное форматирование таблиц.

---

## Структура файлов

| Файл | Содержимое |
|---|---|
| `01_improvements.sql` | `cancel_booking`, `get_flight_info`, триггер `trg_segments_overbooking` |
| `02_demonstration.sql` | Демонстрация: отмена бронирования, ошибки, срабатывание триггера |
| `app.py` | Улучшенное Python-приложение (v2.0) |

---

## Пайплайн запуска в `pgcli`

> ⚠️ Предварительно должны быть применены:
> 1. `lab-3/01_schema_update.sql` (структура БД)
> 2. `lab-5/01_procedure.sql` (процедуры `book_ticket`, `check_free_seats`)

```bash
pg demo
```

```sql
-- 1. Применить улучшения
\i 01_improvements.sql

-- 2. Запустить демонстрацию
\i 02_demonstration.sql
```

**Запуск улучшенного приложения:**
```bash
nix develop   # из корня репозитория
python3 app.py
```

---

## Полный порядок применения всех лаб к чистой базе

```sql
\i ../lab-3/01_schema_update.sql   -- структура (ВПП, блокировка мест, аварийный аэропорт)
\i ../lab-5/01_procedure.sql       -- бронирование
\i ../lab-6/02_optimizations.sql   -- индексы и материализованное представление
\i ../lab-8/01_improvements.sql    -- отмена, get_flight_info, триггер
```
