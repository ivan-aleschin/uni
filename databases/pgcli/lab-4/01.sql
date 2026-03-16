-- 1. Вывести ранжированный список самолетов по требуемой длине ВПП (Оконная функция), 
-- и количество аэропортов назначения, которые могут их принять (Группировка, Подзапрос, JOIN > 3 таблиц)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    a.model, 
    a.min_runway_length,
    DENSE_RANK() OVER (ORDER BY a.min_runway_length DESC NULLS LAST) as runway_rank,
    COUNT(DISTINCT r.arrival_airport) as suitable_destinations
FROM airplanes a
JOIN routes r ON a.airplane_code = r.airplane_code
JOIN airports_data ap ON r.arrival_airport = ap.airport_code
WHERE a.min_runway_length <= ap.max_runway_length
GROUP BY a.model, a.min_runway_length;
