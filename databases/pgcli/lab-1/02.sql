SET search_path = bookings;

WITH seat_counts AS (
    SELECT
        a.airplane_code,
        a.model,
        COUNT(s.seat_no) AS seats
    FROM airplanes a
    JOIN seats s ON s.airplane_code = a.airplane_code
    GROUP BY a.airplane_code, a.model
)
SELECT *, 'maximum' AS type FROM seat_counts WHERE seats = (SELECT MAX(seats) FROM seat_counts)
UNION ALL
SELECT *, 'minimum' AS type FROM seat_counts WHERE seats = (SELECT MIN(seats) FROM seat_counts);
