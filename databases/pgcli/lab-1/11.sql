SET search_path = bookings;

SELECT
    t.passenger_name,
    SUM(f.actual_arrival - f.actual_departure)          AS total_time,
    EXTRACT(EPOCH FROM SUM(f.actual_arrival - f.actual_departure)) / 3600 AS hours
FROM tickets t
JOIN segments s ON s.ticket_no = t.ticket_no
JOIN flights f  ON f.flight_id = s.flight_id
WHERE t.passenger_name = 'Lori Beasley'
    AND f.scheduled_departure >= '2025-10-01 00:00:00+03'
    AND f.scheduled_departure <  '2025-11-01 00:00:00+03'
    AND f.actual_departure IS NOT NULL
GROUP BY t.passenger_name;
