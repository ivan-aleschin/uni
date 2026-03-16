-- 4. Статистика причин перенаправлений рейсов: количество рейсов по каждой причине
-- и её доля от общего числа перенаправлений (Оконная функция с агрегацией, Группировка)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    f.divert_reason,
    COUNT(f.flight_id) as flights_count,
    ROUND(COUNT(f.flight_id) * 100.0 / SUM(COUNT(f.flight_id)) OVER(), 2) as percentage
FROM flights f
JOIN routes r ON f.route_no = r.route_no
JOIN airports a ON r.arrival_airport = a.airport_code
WHERE f.divert_reason IS NOT NULL
GROUP BY f.divert_reason
ORDER BY flights_count DESC;
