SET search_path = bookings;

SELECT
    airport_code,
    airport_name,
    city,
    coordinates
FROM airports
WHERE country = 'China'
    AND coordinates[1] < (
        SELECT coordinates[1]
        FROM airports
        WHERE airport_name LIKE '%Baise%'
    )
ORDER BY coordinates[1];
