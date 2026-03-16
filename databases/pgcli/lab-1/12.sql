SET search_path = bookings;

SELECT COUNT(DISTINCT t.passenger_id) AS passengers
FROM tickets t
JOIN segments s   ON s.ticket_no = t.ticket_no
JOIN flights f ON f.flight_id = s.flight_id
JOIN routes r ON r.route_no = f.route_no
JOIN airports dep ON dep.airport_code = r.departure_airport
JOIN airports arr ON arr.airport_code = r.arrival_airport
WHERE dep.city = 'Moscow'
    AND arr.city = 'Saint Petersburg'
    AND f.scheduled_departure >= '2025-10-09 00:00:00+03'
    AND f.scheduled_departure <  '2025-10-10 00:00:00+03'
    AND s.price < 4000;
