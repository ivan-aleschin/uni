-- Лабораторная работа 6: Создание индексов и материализованного представления
SET search_path = bookings;

-- ============================================================
-- Оптимизация 1: Индекс по имени пассажира
-- Цель: ускорить фильтрацию WHERE passenger_name = '...'
--       в запросах lab-1/11, lab-1/03 и аналогичных
-- До:   Parallel Seq Scan, фильтр отсекает ~991 тыс строк,
--       время ~40 мс
-- После: Index Scan — находит нужные строки напрямую
-- ============================================================
CREATE INDEX IF NOT EXISTS tickets_passenger_name_idx
    ON tickets(passenger_name);

-- ============================================================
-- Оптимизация 2: Покрывающий индекс по passenger_id + passenger_name
-- Цель: ускорить GROUP BY passenger_id, passenger_name в CTE
--       (запрос lab-1/09) и JOIN ON tickets.passenger_id = ...
-- Покрывающий (covering) индекс позволяет выполнить агрегацию
-- без обращения к основной куче таблицы (Index Only Scan)
-- До:   два Seq Scan на tickets (~3 млн строк каждый),
--       сброс агрегации на диск ~161 МБ, время ~1 сек
-- После: Index Only Scan, без сброса на диск
-- ============================================================
CREATE INDEX IF NOT EXISTS tickets_passenger_id_name_idx
    ON tickets(passenger_id, passenger_name);

-- ============================================================
-- Оптимизация 3: Материализованное представление для агрегации
-- Цель: полностью исключить JOIN + GROUP BY при запросе
--       "аэропорт с максимальным числом прилётов" (lab-1/05)
-- Материализованное представление хранит результат агрегации
-- физически на диске и обновляется командой REFRESH.
-- До:   Hash Join flights × routes × airports, ~17 мс
-- После: Seq Scan на маленькой (~73 строки) mv, < 0.1 мс
-- Уникальный индекс нужен для REFRESH CONCURRENTLY (без блокировки)
-- ============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_airport_incoming_flights AS
SELECT
    a.airport_code,
    a.airport_name,
    COUNT(f.flight_id) AS flights_received
FROM airports_data a
JOIN routes  r ON r.arrival_airport = a.airport_code
JOIN flights f ON f.route_no = r.route_no
GROUP BY a.airport_code, a.airport_name;

CREATE UNIQUE INDEX IF NOT EXISTS mv_airport_incoming_flights_pkey
    ON mv_airport_incoming_flights(airport_code);

-- Сбор актуальной статистики для планировщика
ANALYZE tickets;
ANALYZE flights;

SELECT 'Индексы и материализованное представление созданы.';
SELECT 'Для обновления mv при изменении данных: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_airport_incoming_flights;';
