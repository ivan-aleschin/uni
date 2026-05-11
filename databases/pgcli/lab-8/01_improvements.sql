-- Лабораторная работа 8: Доработка процедур и структуры БД
SET search_path = bookings;

-- ============================================================
-- 1. Процедура отмены бронирования
-- Удаляет сегменты, билет и само бронирование.
-- Бронирование нельзя отменить, если рейс уже не Scheduled/On Time.
-- ============================================================
CREATE OR REPLACE FUNCTION cancel_booking(p_book_ref TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_flight_status TEXT;
    v_flight_id     INT;
    v_ticket_no     TEXT;
BEGIN
    -- Проверяем, что бронирование существует
    IF NOT EXISTS (SELECT 1 FROM bookings WHERE book_ref = p_book_ref) THEN
        RAISE EXCEPTION 'Бронирование «%» не найдено', p_book_ref;
    END IF;

    -- Проверяем статус рейса (отмена возможна только до вылета)
    SELECT s.flight_id, f.status, t.ticket_no
    INTO v_flight_id, v_flight_status, v_ticket_no
    FROM tickets t
    JOIN segments s ON s.ticket_no = t.ticket_no
    JOIN flights  f ON f.flight_id = s.flight_id
    WHERE t.book_ref = p_book_ref
    LIMIT 1;

    IF v_flight_status NOT IN ('Scheduled', 'On Time') THEN
        RAISE EXCEPTION
            'Нельзя отменить бронирование: рейс % уже имеет статус "%". Отмена возможна только для рейсов Scheduled или On Time',
            v_flight_id, v_flight_status;
    END IF;

    -- Удаляем сегменты, билеты и само бронирование (каскадно по FK нельзя, удаляем вручную)
    DELETE FROM segments WHERE ticket_no IN (
        SELECT ticket_no FROM tickets WHERE book_ref = p_book_ref
    );
    DELETE FROM tickets  WHERE book_ref = p_book_ref;
    DELETE FROM bookings WHERE book_ref = p_book_ref;

    RAISE NOTICE 'Бронирование % успешно отменено', p_book_ref;
END;
$$;


-- ============================================================
-- 2. Функция для получения детальной информации о рейсе
-- Используется в приложении (lab-7/8) вместо сырого JOIN-запроса
-- ============================================================
CREATE OR REPLACE FUNCTION get_flight_info(p_flight_id INT)
RETURNS TABLE (
    flight_id          INT,
    route_no           TEXT,
    departure_airport  CHAR(3),
    arrival_airport    CHAR(3),
    dep_city           TEXT,
    arr_city           TEXT,
    scheduled_dep      TIMESTAMPTZ,
    dep_local          TIMESTAMP,
    status             TEXT,
    total_seats        INT,
    sold_seats         INT,
    free_seats         INT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        f.flight_id,
        f.route_no,
        r.departure_airport,
        r.arrival_airport,
        (dep_ap.city ->> 'ru')::text AS dep_city,
        (arr_ap.city ->> 'ru')::text AS arr_city,
        f.scheduled_departure,
        (f.scheduled_departure AT TIME ZONE dep_ap.timezone)::timestamp AS dep_local,
        f.status,
        (SELECT COUNT(*) FROM seats s
         WHERE s.airplane_code = r.airplane_code)::int AS total_seats,
        (SELECT COUNT(*) FROM segments seg WHERE seg.flight_id = f.flight_id)::int AS sold_seats,
        check_free_seats(f.flight_id) AS free_seats
    FROM flights f
    JOIN routes r ON r.route_no = f.route_no
        AND r.validity @> f.scheduled_departure
    JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
    JOIN airports_data arr_ap ON arr_ap.airport_code = r.arrival_airport
    WHERE f.flight_id = p_flight_id;
$$;


-- ============================================================
-- 3. Триггер-защита от переполнения: не даёт добавить сегмент,
--    если на рейсе не осталось мест.
--    Обеспечивает целостность данных даже при прямых INSERT (минуя book_ticket).
-- ============================================================
CREATE OR REPLACE FUNCTION trg_check_overbooking()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF check_free_seats(NEW.flight_id) <= 0 THEN
        RAISE EXCEPTION
            'Невозможно добавить сегмент: на рейсе % нет свободных мест (все места заняты)',
            NEW.flight_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_segments_overbooking ON segments;
CREATE TRIGGER trg_segments_overbooking
    BEFORE INSERT ON segments
    FOR EACH ROW
    EXECUTE FUNCTION trg_check_overbooking();
