SET search_path = bookings;

SELECT
    r.route_no,
    dep.city        AS origin_city,
    dep.airport_name,
    arr.city        AS destination_city,
    arr.airport_name,
    r.days_of_week,
    r.scheduled_time
FROM routes r
JOIN airports dep ON dep.airport_code = r.departure_airport
JOIN airports arr ON arr.airport_code = r.arrival_airport
WHERE (dep.city = 'Moscow'          AND arr.city = 'Saint Petersburg'
    OR dep.city = 'Saint Petersburg' AND arr.city = 'Moscow')
    AND r.days_of_week && ARRAY[6, 7]
ORDER BY dep.city, r.scheduled_time;
