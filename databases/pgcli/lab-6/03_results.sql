-- Лабораторная работа 6: Состояние запросов ПОСЛЕ оптимизации
-- Запустить ПОСЛЕ 02_optimizations.sql
SET search_path = bookings;

-- ============================================================
-- Запрос 1 (из lab-1/11): ПОСЛЕ — индекс по passenger_name
-- Ожидаем: Index Scan вместо Parallel Seq Scan,
--          время должно упасть с ~40 мс до < 1 мс
-- ============================================================
\echo '=== Запрос 1 (lab-1/11): ПОСЛЕ оптимизации ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    t.passenger_name,
    SUM(f.actual_arrival - f.actual_departure) AS total_time,
    EXTRACT(EPOCH FROM SUM(f.actual_arrival - f.actual_departure)) / 3600 AS hours
FROM tickets t
JOIN segments s ON s.ticket_no = t.ticket_no
JOIN flights f  ON f.flight_id = s.flight_id
WHERE t.passenger_name = 'Lori Beasley'
  AND f.scheduled_departure >= '2025-10-01 00:00:00+03'
  AND f.scheduled_departure <  '2025-11-01 00:00:00+03'
  AND f.actual_departure IS NOT NULL
GROUP BY t.passenger_name;

-- ============================================================
-- Запрос 2 (из lab-1/09): ПОСЛЕ — покрывающий индекс
-- Ожидаем: Index Only Scan на CTE,
--          отсутствие сброса агрегации на диск,
--          время должно упасть с ~1000 мс до < 100 мс
-- ============================================================
\echo '=== Запрос 2 (lab-1/09): ПОСЛЕ оптимизации ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
WITH passengers_5 AS (
    SELECT passenger_id, passenger_name
    FROM tickets
    GROUP BY passenger_id, passenger_name
    HAVING COUNT(*) = 5
)
SELECT DISTINCT
    p.passenger_name,
    dep.city AS origin_city,
    arr.city AS destination_city
FROM passengers_5 p
JOIN tickets  t   ON t.passenger_id = p.passenger_id
JOIN segments s   ON s.ticket_no = t.ticket_no
JOIN flights  f   ON f.flight_id = s.flight_id
JOIN routes   r   ON r.route_no = f.route_no
JOIN airports dep ON dep.airport_code = r.departure_airport
JOIN airports arr ON arr.airport_code = r.arrival_airport
ORDER BY p.passenger_name;

-- ============================================================
-- Запрос 3 (из lab-1/05): ПОСЛЕ — материализованное представление
-- Оригинальный запрос не меняется — планировщик сам не использует mv.
-- Показываем ПЕРЕПИСАННЫЙ вариант с явным обращением к mv:
-- ============================================================
\echo '=== Запрос 3 (lab-1/05): ПОСЛЕ оптимизации — через mv ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT airport_code, airport_name, flights_received
FROM mv_airport_incoming_flights
ORDER BY flights_received DESC
LIMIT 1;

-- Для сравнения — фактический результат обоих вариантов совпадает:
\echo '--- Результат оригинального запроса ---'
SELECT a.airport_code, a.airport_name, COUNT(f.flight_id) AS flights_received
FROM airports a
JOIN routes r  ON r.arrival_airport = a.airport_code
JOIN flights f ON f.route_no = r.route_no
GROUP BY a.airport_code, a.airport_name
ORDER BY flights_received DESC
LIMIT 1;

\echo '--- Результат через материализованное представление ---'
SELECT airport_code, airport_name, flights_received
FROM mv_airport_incoming_flights
ORDER BY flights_received DESC
LIMIT 1;
