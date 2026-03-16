-- 6. Рейсы, у которых есть заблокированные места. Для каждого рейса показываем,
-- сколько всего мест на самолете (через подзапрос) и процент заблокированных (Группировка, Подзапрос в SELECT)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    f.flight_id, 
    r.route_no,
    r.airplane_code,
    COUNT(bs.seat_no) as blocked_seats,
    (SELECT COUNT(*) FROM seats s WHERE s.airplane_code = r.airplane_code) as total_seats,
    ROUND(COUNT(bs.seat_no) * 100.0 / (SELECT COUNT(*) FROM seats s WHERE s.airplane_code = r.airplane_code), 2) as blocked_pct
FROM flights f
JOIN flight_blocked_seats bs ON f.flight_id = bs.flight_id
JOIN routes r ON f.route_no = r.route_no
GROUP BY f.flight_id, r.route_no, r.airplane_code
ORDER BY blocked_pct DESC;
