-- 10. Найти самолеты, выполняющие перенаправленные рейсы, и показать,
-- какая часть их рейсов завершилась не по плану, с общим итогом (Оконные функции SUM, COUNT)
SET search_path = bookings;
SET bookings.lang = 'ru';

SELECT DISTINCT
    pl.model,
    COUNT(f.flight_id) OVER (PARTITION BY pl.model) as diverted_count_for_model,
    COUNT(f.flight_id) OVER () as total_diverted_flights,
    ROUND(COUNT(f.flight_id) OVER (PARTITION BY pl.model) * 100.0 / COUNT(f.flight_id) OVER (), 2) as model_divert_pct
FROM flights f
JOIN routes r ON f.route_no = r.route_no
JOIN airplanes pl ON r.airplane_code = pl.airplane_code
WHERE f.divert_reason IS NOT NULL
ORDER BY diverted_count_for_model DESC;
