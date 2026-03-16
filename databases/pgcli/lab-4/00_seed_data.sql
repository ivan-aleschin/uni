SET search_path = bookings;
SET bookings.lang = 'ru';

-- Добавим немного моковых данных, чтобы наши 10 осмысленных запросов выдавали красивые результаты
-- (длины ВПП)
UPDATE airplanes_data SET min_runway_length = 2000 WHERE airplane_code IN ('319', '320', '321', '733');
UPDATE airplanes_data SET min_runway_length = 3300 WHERE airplane_code IN ('77W', '763', '351');
UPDATE airplanes_data SET min_runway_length = 1500 WHERE airplane_code IN ('CR2', 'SU9');

UPDATE airports_data SET max_runway_length = 3800 WHERE airport_code IN ('SVO', 'DME', 'VKO', 'LED');
UPDATE airports_data SET max_runway_length = 2500 WHERE airport_code IN ('KZN', 'SVX', 'AER');
UPDATE airports_data SET max_runway_length = 1800 WHERE airport_code IN ('BKA', 'OSF', 'BZK');

-- (заблокированные места)
INSERT INTO flight_blocked_seats (flight_id, seat_no, reason)
SELECT flight_id, '1A', 'Техническая неисправность кресла' FROM flights ORDER BY flight_id LIMIT 10
ON CONFLICT DO NOTHING;

INSERT INTO flight_blocked_seats (flight_id, seat_no, reason)
SELECT flight_id, '1B', 'Резерв для экипажа' FROM flights ORDER BY flight_id OFFSET 5 LIMIT 8
ON CONFLICT DO NOTHING;

-- (перенаправленные рейсы)
UPDATE flights SET actual_arrival_airport = 'SVO', divert_reason = 'Густой туман'
WHERE flight_id IN (SELECT f.flight_id FROM flights f JOIN routes r ON f.route_no = r.route_no WHERE f.status = 'Arrived' AND r.arrival_airport != 'SVO' ORDER BY f.flight_id LIMIT 5);

UPDATE flights SET actual_arrival_airport = 'KZN', divert_reason = 'Снежная буря'
WHERE flight_id IN (SELECT f.flight_id FROM flights f JOIN routes r ON f.route_no = r.route_no WHERE f.status = 'Arrived' AND r.arrival_airport != 'KZN' ORDER BY f.flight_id OFFSET 10 LIMIT 3);
