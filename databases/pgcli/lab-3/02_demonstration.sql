SET search_path = bookings;
-- Устанавливаем язык сессии для корректного отображения названий аэропортов и самолетов
SET bookings.lang = 'ru';

-- Демонстрация задания 1: Зададим минимальную длину ВПП для Боинга 777-300 и длину ВПП во Внуково
UPDATE airplanes_data
SET min_runway_length = 3300
WHERE airplane_code = '77W';

UPDATE airports_data
SET max_runway_length = 3500
WHERE airport_code = 'VKO';

-- Выведем результат:
SELECT airport_code, airport_name, max_runway_length
FROM airports
WHERE airport_code = 'VKO';

SELECT airplane_code, model, min_runway_length
FROM airplanes
WHERE airplane_code = '77W';


-- Демонстрация задания 2: Заблокируем места 1A и 1B на первый попавшийся рейс
INSERT INTO flight_blocked_seats (flight_id, seat_no, reason)
VALUES
    ((SELECT flight_id FROM flights ORDER BY flight_id LIMIT 1), '1A', 'Сломано кресло'),
    ((SELECT flight_id FROM flights ORDER BY flight_id LIMIT 1), '1B', 'Сломано кресло')
ON CONFLICT (flight_id, seat_no) DO UPDATE SET reason = EXCLUDED.reason;

SELECT f.flight_id, f.route_no, bs.seat_no, bs.reason
FROM flight_blocked_seats bs
JOIN flights f ON f.flight_id = bs.flight_id;


-- Демонстрация задания 3: Рейс перенаправлен в запасной аэропорт
-- Возьмем рейс из представления timetable, который прибыл
UPDATE flights
SET actual_arrival_airport = 'SVO',
    divert_reason = 'Метеоусловия в порту назначения'
WHERE flight_id = (
    SELECT flight_id FROM timetable
    WHERE arrival_airport = 'LED' AND status = 'Arrived'
    ORDER BY flight_id
    LIMIT 1
);

-- Выведем результат из нашего нового представления timetable
SELECT flight_id, route_no, scheduled_arrival_local, arrival_airport,
       actual_arrival_airport, divert_reason
FROM timetable
WHERE divert_reason IS NOT NULL;
