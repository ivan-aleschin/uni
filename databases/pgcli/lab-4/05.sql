-- 5. Для каждого аэропорта вывести максимальную длину ВПП и сравнить с требуемой ВПП
-- самого "требовательного" самолета, который летит туда по расписанию (Оконная функция, Подзапрос)
SET search_path = bookings;
SET bookings.lang = 'ru';

WITH AirportPlaneReqs AS (
    SELECT 
        ap.airport_name, 
        ap.max_runway_length,
        a.model,
        a.min_runway_length,
        RANK() OVER (PARTITION BY ap.airport_code ORDER BY a.min_runway_length DESC NULLS LAST) as req_rank
    FROM airports ap
    JOIN routes r ON ap.airport_code = r.arrival_airport
    JOIN airplanes a ON r.airplane_code = a.airplane_code
)
SELECT 
    airport_name, 
    max_runway_length, 
    model as most_demanding_plane, 
    min_runway_length as required_runway
FROM AirportPlaneReqs
WHERE req_rank = 1 AND max_runway_length IS NOT NULL
ORDER BY max_runway_length DESC;
