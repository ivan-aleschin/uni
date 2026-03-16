SET search_path = bookings;
SET bookings.lang = 'ru';

WITH passengers_5 AS (
    SELECT passenger_id, passenger_name
    FROM tickets
    GROUP BY passenger_id, passenger_name
    HAVING COUNT(*) = 5
)
SELECT DISTINCT
    p.passenger_name,
    dep.city   AS origin_city,
    arr.city   AS destination_city
FROM passengers_5 p
JOIN tickets t      ON t.passenger_id = p.passenger_id
JOIN segments s     ON s.ticket_no = t.ticket_no
JOIN flights f      ON f.flight_id = s.flight_id
JOIN routes r       ON r.route_no = f.route_no
JOIN airports dep   ON dep.airport_code = r.departure_airport
JOIN airports arr   ON arr.airport_code = r.arrival_airport
ORDER BY p.passenger_name;
