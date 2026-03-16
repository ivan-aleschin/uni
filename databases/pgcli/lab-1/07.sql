SET search_path = bookings;

-- 3 = Wednesday in days_of_week
SELECT
    r.route_no,
    r.days_of_week,
    r.scheduled_time,
    r.duration
FROM routes r
WHERE r.departure_airport = 'SVO'
    AND r.arrival_airport = 'KZN'
    AND 3 = ANY(r.days_of_week);
