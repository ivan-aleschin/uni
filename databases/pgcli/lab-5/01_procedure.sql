SET search_path = bookings;

-- Последовательность для генерации уникальных номеров билетов
-- Начинаем после максимального существующего ticket_no в базе (0005434990767)
CREATE SEQUENCE IF NOT EXISTS ticket_no_seq
    START WITH 5435000000
    INCREMENT BY 1
    NO MAXVALUE
    CACHE 1;

-- Функция: количество свободных мест на рейсе
-- Возвращает: (места самолёта по маршруту) - (уже проданные сегменты)
CREATE OR REPLACE FUNCTION check_free_seats(p_flight_id INT)
RETURNS INT
LANGUAGE sql
STABLE
AS $$
    SELECT
        (SELECT COUNT(*)
         FROM seats s
         JOIN routes r ON r.airplane_code = s.airplane_code
           AND r.validity @> f.scheduled_departure
         WHERE r.route_no = f.route_no
        )::int
        -
        (SELECT COUNT(*) FROM segments seg WHERE seg.flight_id = p_flight_id)::int
    FROM flights f
    WHERE f.flight_id = p_flight_id;
$$;

-- Вспомогательная функция: генерация случайного 6-символьного кода бронирования
CREATE OR REPLACE FUNCTION gen_book_ref()
RETURNS CHAR(6)
LANGUAGE sql
VOLATILE
AS $$
    SELECT string_agg(
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
               (floor(random() * 36) + 1)::int, 1),
        ''
    )
    FROM generate_series(1, 6);
$$;

-- Процедура бронирования билета
-- Параметры:
--   p_passenger_id    -- идентификатор документа пассажира (например: 'RU 1234567890123')
--   p_passenger_name  -- имя пассажира на латинице (например: 'Ivan Petrov')
--   p_flight_id       -- ID рейса (из таблицы flights)
--   p_fare_conditions -- класс обслуживания: 'Economy', 'Comfort' или 'Business'
--   p_price           -- цена билета в рублях
-- Возвращает: код бронирования (book_ref), либо бросает исключение
CREATE OR REPLACE FUNCTION book_ticket(
    p_passenger_id    TEXT,
    p_passenger_name  TEXT,
    p_flight_id       INT,
    p_fare_conditions TEXT DEFAULT 'Economy',
    p_price           NUMERIC DEFAULT 0
) RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_book_ref   CHAR(6);
    v_ticket_no  TEXT;
    v_free_seats INT;
    v_status     TEXT;
BEGIN
    -- Проверка допустимого класса обслуживания
    IF p_fare_conditions NOT IN ('Economy', 'Comfort', 'Business') THEN
        RAISE EXCEPTION
            'Недопустимый класс обслуживания: %. Допустимые значения: Economy, Comfort, Business',
            p_fare_conditions;
    END IF;

    -- Проверка существования рейса и его статуса
    SELECT status INTO v_status
    FROM flights
    WHERE flight_id = p_flight_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Рейс с ID % не найден', p_flight_id;
    END IF;

    IF v_status NOT IN ('Scheduled', 'On Time') THEN
        RAISE EXCEPTION
            'Рейс % недоступен для бронирования. Текущий статус: "%". Бронирование возможно только для рейсов со статусом Scheduled или On Time',
            p_flight_id, v_status;
    END IF;

    -- Проверка наличия свободных мест
    v_free_seats := check_free_seats(p_flight_id);
    IF v_free_seats IS NULL OR v_free_seats <= 0 THEN
        RAISE EXCEPTION
            'На рейсе % нет свободных мест. Все % мест заняты',
            p_flight_id, -COALESCE(v_free_seats, 0);
    END IF;

    -- Генерация уникального кода бронирования (цикл на случай коллизии)
    LOOP
        v_book_ref := gen_book_ref();
        EXIT WHEN NOT EXISTS (SELECT 1 FROM bookings WHERE book_ref = v_book_ref);
    END LOOP;

    -- Генерация номера билета через последовательность, дополненный нулями до 13 символов
    v_ticket_no := lpad(nextval('ticket_no_seq')::text, 13, '0');

    -- Вставка бронирования
    INSERT INTO bookings (book_ref, book_date, total_amount)
    VALUES (v_book_ref, now(), p_price);

    -- Вставка билета (outbound = TRUE — прямой рейс)
    INSERT INTO tickets (ticket_no, book_ref, passenger_id, passenger_name, outbound)
    VALUES (v_ticket_no, v_book_ref, p_passenger_id, p_passenger_name, TRUE);

    -- Вставка сегмента (конкретного перелёта в составе билета)
    INSERT INTO segments (ticket_no, flight_id, fare_conditions, price)
    VALUES (v_ticket_no, p_flight_id, p_fare_conditions, p_price);

    RETURN v_book_ref;
END;
$$;
