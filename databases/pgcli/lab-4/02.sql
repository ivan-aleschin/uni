-- 2. Найти рейсы, у которых количество заблокированных мест превышает среднее 
-- по всем проблемным рейсам (Подзапрос в HAVING, Группировка, JOIN > 3 таблиц)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    f.flight_id, 
    f.route_no, 
    a.airport_name as departure_airport,
    COUNT(bs.seat_no) as blocked_seats_count
FROM flights f
JOIN flight_blocked_seats bs ON f.flight_id = bs.flight_id
JOIN routes r ON f.route_no = r.route_no
JOIN airports a ON r.departure_airport = a.airport_code
GROUP BY f.flight_id, f.route_no, a.airport_name
HAVING COUNT(bs.seat_no) > (
    SELECT AVG(cnt) FROM (
        SELECT COUNT(seat_no) as cnt 
        FROM flight_blocked_seats 
        GROUP BY flight_id
    ) as sub
)
ORDER BY blocked_seats_count DESC;
