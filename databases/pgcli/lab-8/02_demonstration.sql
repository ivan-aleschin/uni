SET search_path = bookings;
SET bookings.lang = 'ru';

-- ============================================================
-- Шаг 1. Информация о рейсе через новую функцию get_flight_info
-- ============================================================
SELECT '=== get_flight_info(12136) ===';
SELECT * FROM get_flight_info(12136);

-- ============================================================
-- Шаг 2. Бронируем билет, потом отменяем его
-- ============================================================
SELECT '=== Бронирование и отмена ===';
DO $$
DECLARE
    v_book_ref TEXT;
BEGIN
    -- Создаём тестовое бронирование
    v_book_ref := book_ticket('RU 0000000000001', 'Test Cancel User', 12136, 'Economy', 2000);
    RAISE NOTICE 'Создано бронирование: %', v_book_ref;

    -- Отменяем его
    PERFORM cancel_booking(v_book_ref);

    -- Проверяем, что бронирования больше нет
    IF NOT EXISTS (SELECT 1 FROM bookings WHERE book_ref = v_book_ref) THEN
        RAISE NOTICE 'Подтверждено: бронирование % удалено из базы', v_book_ref;
    END IF;
END;
$$;

-- ============================================================
-- Шаг 3. Демонстрация ошибки: отмена несуществующего бронирования
-- ============================================================
DO $$
BEGIN
    PERFORM cancel_booking('ZZZZZZ');
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Ожидаемая ошибка: %', SQLERRM;
END;
$$;

-- ============================================================
-- Шаг 4. Демонстрация триггера-защиты от переполнения
-- Попытка напрямую вставить сегмент в полный рейс
-- (используем рейс с 0 свободных мест для теста)
-- ============================================================
SELECT '=== Триггер защиты от переполнения ===';
DO $$
DECLARE
    v_full_flight_id INT;
    v_fake_ticket    TEXT := '0000000000001';
BEGIN
    -- Найдём рейс, где уже нет мест
    SELECT f.flight_id INTO v_full_flight_id
    FROM flights f
    WHERE f.status IN ('Scheduled', 'On Time')
      AND check_free_seats(f.flight_id) = 0
    LIMIT 1;

    IF v_full_flight_id IS NULL THEN
        RAISE NOTICE 'Нет полностью занятых рейсов для теста триггера';
        RETURN;
    END IF;

    -- Вставляем временный «фиктивный» билет, чтобы можно было добавить сегмент
    INSERT INTO bookings (book_ref, book_date, total_amount) VALUES ('ZZTRIG', now(), 0);
    INSERT INTO tickets  (ticket_no, book_ref, passenger_id, passenger_name, outbound)
    VALUES (v_fake_ticket, 'ZZTRIG', 'XX 0000000000000', 'Trigger Test', TRUE);

    -- Попытка добавить сегмент на переполненный рейс
    BEGIN
        INSERT INTO segments (ticket_no, flight_id, fare_conditions, price)
        VALUES (v_fake_ticket, v_full_flight_id, 'Economy', 0);
        RAISE NOTICE 'Вставка прошла (не должно было случиться)';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Триггер сработал: %', SQLERRM;
    END;

    -- Чистим тестовые данные
    DELETE FROM tickets  WHERE book_ref = 'ZZTRIG';
    DELETE FROM bookings WHERE book_ref = 'ZZTRIG';
END;
$$;
