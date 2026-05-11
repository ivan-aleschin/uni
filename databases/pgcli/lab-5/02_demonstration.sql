SET search_path = bookings;
SET bookings.lang = 'ru';

-- ====================================================================
-- Шаг 1. Показываем несколько доступных рейсов со свободными местами
-- ====================================================================
SELECT
    f.flight_id,
    f.route_no,
    r.departure_airport AS dep,
    r.arrival_airport   AS arr,
    f.scheduled_departure AT TIME ZONE dep_ap.timezone AS departure_local,
    f.status,
    check_free_seats(f.flight_id) AS free_seats
FROM flights f
JOIN routes r ON r.route_no = f.route_no
    AND r.validity @> f.scheduled_departure
JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
WHERE f.status IN ('Scheduled', 'On Time')
  AND check_free_seats(f.flight_id) > 0
ORDER BY f.scheduled_departure
LIMIT 10;

-- ====================================================================
-- Шаг 2. Проверяем количество свободных мест на конкретном рейсе (12136)
-- ====================================================================
SELECT
    f.flight_id,
    f.route_no,
    f.status,
    (SELECT COUNT(*) FROM seats s
     JOIN routes r ON r.airplane_code = s.airplane_code
       AND r.validity @> f.scheduled_departure
     WHERE r.route_no = f.route_no) AS total_seats,
    (SELECT COUNT(*) FROM segments seg WHERE seg.flight_id = f.flight_id) AS sold_seats,
    check_free_seats(f.flight_id) AS free_seats
FROM flights f
WHERE f.flight_id = 12136;

-- ====================================================================
-- Шаг 3. Бронируем три билета на рейс 12136
-- ====================================================================
SELECT book_ticket('RU 1234567890123', 'Ivan Petrov',    12136, 'Economy', 4500.00) AS book_ref_1;
SELECT book_ticket('DE 9876543210987', 'Klaus Mueller',  12136, 'Business', 18000.00) AS book_ref_2;
SELECT book_ticket('US 5555555555555', 'Jane Smith',     12136, 'Comfort', 8500.00) AS book_ref_3;

-- ====================================================================
-- Шаг 4. Проверяем, что бронирования появились в базе
-- ====================================================================
SELECT
    b.book_ref,
    b.book_date,
    b.total_amount,
    t.ticket_no,
    t.passenger_name,
    s.fare_conditions,
    s.price,
    s.flight_id
FROM bookings b
JOIN tickets t  ON t.book_ref = b.book_ref
JOIN segments s ON s.ticket_no = t.ticket_no
WHERE b.book_date >= now() - interval '1 minute'
ORDER BY b.book_date;

-- ====================================================================
-- Шаг 5. Проверяем, что количество свободных мест уменьшилось на 3
-- ====================================================================
SELECT
    check_free_seats(12136) AS free_seats_after_booking;

-- ====================================================================
-- Шаг 6. Демонстрация ошибки: бронирование на несуществующий рейс
-- ====================================================================
DO $$
BEGIN
    PERFORM book_ticket('XX 0000000000000', 'Ghost Passenger', 99999999, 'Economy', 1000);
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Ожидаемая ошибка: %', SQLERRM;
END;
$$;

-- ====================================================================
-- Шаг 7. Демонстрация ошибки: недопустимый класс обслуживания
-- ====================================================================
DO $$
BEGIN
    PERFORM book_ticket('RU 1111111111111', 'Test User', 12136, 'Vip', 99999);
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Ожидаемая ошибка: %', SQLERRM;
END;
$$;
