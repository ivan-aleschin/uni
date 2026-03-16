-- 9. Список аэропортов, принявших перенаправленные рейсы, с расчетом
-- средней задержки (между фактическим и плановым временем) для этих рейсов (Группировка, Подзапрос в FROM)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT 
    a.airport_name,
    a.city,
    diverts.flights_received,
    diverts.avg_delay
FROM airports a
JOIN (
    SELECT 
        actual_arrival_airport,
        COUNT(*) as flights_received,
        AVG(actual_arrival - scheduled_arrival) as avg_delay
    FROM flights
    WHERE divert_reason IS NOT NULL
    GROUP BY actual_arrival_airport
) as diverts ON a.airport_code = diverts.actual_arrival_airport
ORDER BY diverts.flights_received DESC;
