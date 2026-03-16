SET search_path = bookings;

WITH flight_info AS (
    SELECT 
        f.flight_id, 
        f.route_no,
        f.scheduled_departure_local,
        f.airplane_code,
        (SELECT COUNT(*) FROM seats s WHERE s.airplane_code = f.airplane_code) AS total_seats,
        (SELECT COUNT(*) FROM boarding_passes bp WHERE bp.flight_id = f.flight_id) AS booked_seats
    FROM timetable f
    WHERE f.route_no = 'PG0035'
      AND f.scheduled_departure_local >= '2025-10-01'
      AND f.scheduled_departure_local < '2025-10-02'
)
SELECT 
    flight_id,
    route_no,
    scheduled_departure_local,
    total_seats,
    booked_seats,
    (total_seats - booked_seats) AS free_seats
FROM flight_info;
