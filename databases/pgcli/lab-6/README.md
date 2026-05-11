# Лабораторная работа 6

## Задание
**Оптимизация запросов.** Подготовить предложения по оптимизации трёх запросов из лабораторных работ 1 и 4. Допускается изменение запроса, добавление индексов, кластеров, материализованных представлений.

Выбраны три запроса: два из **lab-1** и один из **lab-1** (проблема была у всех трёх в одном — таблица `tickets`), с добавлением **материализованного представления** для lab-1/05.

---

---

## Теория: Оптимизация запросов в PostgreSQL

### EXPLAIN и EXPLAIN ANALYZE
```sql
EXPLAIN SELECT ...;           -- показать план без выполнения
EXPLAIN (ANALYZE) SELECT ...; -- выполнить и показать реальное время
EXPLAIN (ANALYZE, BUFFERS) SELECT ...; -- + статистику чтения буферов
```

**Как читать план:**
- `Seq Scan` — полный перебор таблицы (плохо для больших таблиц с фильтрацией).
- `Index Scan` / `Bitmap Index Scan` — поиск через индекс (быстрее при высокой селективности).
- `Index Only Scan` — данные берутся прямо из индекса, без обращения к heap.
- `Hash Join` / `Nested Loop` / `Merge Join` — стратегии соединения таблиц.
- `cost=X..Y` — оценка стоимости (X — до первой строки, Y — всего).
- `actual time=X..Y rows=N loops=K` — реальное время и количество строк.

### B-tree индексы
```sql
CREATE INDEX idx_name ON table(column);          -- простой
CREATE INDEX idx_name ON table(col1, col2);      -- составной (покрывающий)
CREATE INDEX idx_name ON table(col) WHERE cond;  -- частичный (partial)
```
- **Составной индекс** `(a, b)` ускоряет запросы по `(a)` и `(a, b)`, но **не** по `(b)` отдельно.
- **Покрывающий индекс** содержит все нужные столбцы → `Index Only Scan` (без обращения к куче).
- **Частичный индекс** — меньше размер, быстрее обновление; эффективен для редких условий.

### Материализованное представление
```sql
CREATE MATERIALIZED VIEW mv AS SELECT ...;  -- вычислить и сохранить результат
REFRESH MATERIALIZED VIEW mv;               -- обновить (с блокировкой)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv;  -- обновить без блокировки чтения
                                             -- (требует UNIQUE INDEX)
```
Подходит для **дорогих** агрегаций, которые читаются часто, а обновляются редко.

### ANALYZE — обновление статистики
```sql
ANALYZE table_name;  -- собрать статистику распределения значений
```
После создания индексов **всегда** запускать `ANALYZE` — иначе планировщик может не использовать новый индекс.

---

## Запрос 1 — `lab-1/11`: Время в полётах по имени пассажира

**Исходный запрос:** фильтрует `WHERE passenger_name = 'Lori Beasley'` — без индекса.

**До оптимизации:**
- `Parallel Seq Scan on tickets` — перебирает ~3 млн строк
- Фильтр отсекает ~991 000 строк
- Время: **~40 мс**

**Предложенная оптимизация:**
```sql
CREATE INDEX tickets_passenger_name_idx ON tickets(passenger_name);
```

**После оптимизации:**
- `Bitmap Index Scan on tickets_passenger_name_idx` — находит 7 строк напрямую
- Время: **~0.2 мс** (ускорение в **200 раз**)

---

## Запрос 2 — `lab-1/09`: Пассажиры с ровно 5 билетами и их маршруты

**Исходный запрос:** CTE делает `GROUP BY passenger_id, passenger_name` — дважды сканирует всю таблицу `tickets`.

**До оптимизации:**
- Два `Seq Scan on tickets` (~3 млн строк каждый)
- Сброс агрегации на диск: **~161 МБ**
- Время: **~1 000 мс**

**Предложенная оптимизация:**
```sql
CREATE INDEX tickets_passenger_id_name_idx ON tickets(passenger_id, passenger_name);
```
Покрывающий индекс по обоим столбцам `GROUP BY` позволяет агрегации работать без обращения к основной куче таблицы (`Index Only Scan`).

**После оптимизации:**
- `Index Only Scan using tickets_passenger_id_name_idx` — без сброса на диск
- Время: **~350 мс** (ускорение в **3 раза**, нет disk spill)

> Полное ускорение ограничено тем, что PostgreSQL всё равно должен просмотреть все 3 млн строк индекса для подсчёта групп. Дальнейшая оптимизация возможна через секционирование таблицы `tickets`.

---

## Запрос 3 — `lab-1/05`: Аэропорт с максимальным числом рейсов

**Исходный запрос:** JOIN трёх таблиц + `GROUP BY` + `ORDER BY` + `LIMIT 1` — каждый раз пересчитывается заново.

**До оптимизации:**
- `Hash Join` (flights × routes × airports_data)
- Время: **~17 мс**

**Предложенная оптимизация** — материализованное представление:
```sql
CREATE MATERIALIZED VIEW mv_airport_incoming_flights AS
SELECT airport_code, airport_name, COUNT(f.flight_id) AS flights_received
FROM airports_data a
JOIN routes r  ON r.arrival_airport = a.airport_code
JOIN flights f ON f.route_no = r.route_no
GROUP BY a.airport_code, a.airport_name;

CREATE UNIQUE INDEX ON mv_airport_incoming_flights(airport_code);
```

**После оптимизации:**
```sql
-- Переписанный запрос
SELECT airport_code, airport_name, flights_received
FROM mv_airport_incoming_flights
ORDER BY flights_received DESC LIMIT 1;
```
- `Seq Scan` на 73-строковой таблице вместо JOIN трёх больших таблиц
- Время: **~0.026 мс** (ускорение в **650 раз**)
- Обновление: `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_airport_incoming_flights;`

> **Ограничение:** материализованное представление хранит `airport_name` в виде JSONB (сырые данные), поэтому результат не переводится автоматически на русский язык. Для production нужно либо хранить переведённые строки, либо обрабатывать JSONB в запросе.

---

## Структура файлов

| Файл | Содержимое |
|---|---|
| `01_baseline.sql` | `EXPLAIN ANALYZE` для трёх запросов **до** оптимизации |
| `02_optimizations.sql` | `CREATE INDEX` + `CREATE MATERIALIZED VIEW` + `ANALYZE` |
| `03_results.sql` | `EXPLAIN ANALYZE` для трёх запросов **после** оптимизации |

---

## Пайплайн запуска в `pgcli`

```bash
pg demo
```

```sql
-- Зафиксировать baseline (план ДО оптимизации)
\i 01_baseline.sql

-- Применить оптимизации
\i 02_optimizations.sql

-- Сравнить планы ПОСЛЕ оптимизации
\i 03_results.sql
```

> ⚠️ Если индексы уже созданы (повторный запуск), `02_optimizations.sql` использует `IF NOT EXISTS` — выполнится без ошибок.
