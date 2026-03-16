SET search_path = bookings;

SELECT DISTINCT
    a.airport_code,
    a.airport_name,
    a.city,
    a.country
FROM tickets t
JOIN segments s ON s.ticket_no = t.ticket_no
JOIN flights f ON f.flight_id = s.flight_id
JOIN routes r ON r.route_no = f.route_no
JOIN airports a ON a.airport_code IN (r.departure_airport, r.arrival_airport)
WHERE t.passenger_name = 'Zhiming Hou'
ORDER BY a.country, a.city;
