SET search_path = bookings;

SELECT
    tt.flight_id,
    tt.route_no,
    tt.scheduled_departure_local,
    tt.actual_departure_local,
    tt.actual_departure - tt.scheduled_departure AS delay
FROM timetable tt
WHERE tt.departure_airport = 'VKO'
    AND tt.scheduled_departure >= '2025-10-01 00:00:00+03'
    AND tt.scheduled_departure <  '2025-10-02 00:00:00+03'
    AND tt.actual_departure - tt.scheduled_departure > INTERVAL '2 hours'
ORDER BY delay DESC;
