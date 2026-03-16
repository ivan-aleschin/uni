SET search_path = bookings;

SELECT
    a.airport_code,
    a.airport_name,
    COUNT(f.flight_id) as flights_received
FROM airports a
JOIN routes r ON r.arrival_airport = a.airport_code
JOIN flights f ON f.route_no = r.route_no
GROUP BY a.airport_code, a.airport_name
ORDER BY flights_received DESC
LIMIT 1;
