-- 8. Вывести полную информацию по заблокированным местам: номер рейса, место, причину
-- и предыдущую причину на этом же рейсе (используя оконную функцию LAG)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    f.flight_id,
    a.airport_name as departure_airport,
    bs.seat_no,
    bs.reason,
    LAG(bs.reason) OVER (PARTITION BY f.flight_id ORDER BY bs.seat_no) as previous_seat_reason
FROM flight_blocked_seats bs
JOIN flights f ON bs.flight_id = f.flight_id
JOIN routes r ON f.route_no = r.route_no
JOIN airports a ON r.departure_airport = a.airport_code
ORDER BY f.flight_id, bs.seat_no;
