-- 3. Вывести список пассажиров, чей рейс был перенаправлен, и пронумеровать их
-- в рамках каждого нового аэропорта прибытия (Оконная функция, JOIN > 3 таблиц)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    t.passenger_name,
    f.flight_id,
    a_act.airport_name as actual_arrival,
    f.divert_reason,
    ROW_NUMBER() OVER (PARTITION BY f.actual_arrival_airport ORDER BY t.passenger_name) as pass_num_in_airport
FROM tickets t
JOIN segments s ON t.ticket_no = s.ticket_no
JOIN flights f ON s.flight_id = f.flight_id
JOIN airports a_act ON f.actual_arrival_airport = a_act.airport_code
WHERE f.divert_reason IS NOT NULL
ORDER BY actual_arrival, pass_num_in_airport
LIMIT 20; -- Ограничиваем вывод для удобства
