-- 7. Найти "проблемные" маршруты: маршруты, на которых чаще всего происходят перенаправления
-- Выводим маршрут, количество перенаправлений и ранжируем их (Оконная функция, Группировка, Подзапрос)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    sub.route_no,
    sub.dep_airport,
    sub.diverts_count,
    DENSE_RANK() OVER (ORDER BY sub.diverts_count DESC) as trouble_rank
FROM (
    SELECT 
        r.route_no,
        dep.airport_name as dep_airport,
        COUNT(f.flight_id) as diverts_count
    FROM flights f
    JOIN routes r ON f.route_no = r.route_no
    JOIN airports dep ON r.departure_airport = dep.airport_code
    WHERE f.divert_reason IS NOT NULL
    GROUP BY r.route_no, dep.airport_name
) as sub;
