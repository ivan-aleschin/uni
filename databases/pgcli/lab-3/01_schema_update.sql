SET search_path = bookings;

-- Задание 1: Длина ВПП для аэропортов и самолетов
ALTER TABLE airports_data 
ADD COLUMN IF NOT EXISTS max_runway_length INT CHECK (max_runway_length > 0);

ALTER TABLE airplanes_data 
ADD COLUMN IF NOT EXISTS min_runway_length INT CHECK (min_runway_length > 0);

-- Обновляем представления
CREATE OR REPLACE VIEW airports AS
SELECT airport_code,
    airport_name ->> lang() AS airport_name,
    city ->> lang() AS city,
    country ->> lang() AS country,
    coordinates,
    timezone,
    max_runway_length
FROM airports_data ml;

CREATE OR REPLACE VIEW airplanes AS
SELECT airplane_code,
    model ->> lang() AS model,
    range,
    speed,
    min_runway_length
FROM airplanes_data ml;


-- Задание 2: Блокировка мест на рейс
CREATE TABLE IF NOT EXISTS flight_blocked_seats (
    flight_id INT NOT NULL REFERENCES flights(flight_id) ON DELETE CASCADE,
    seat_no VARCHAR(4) NOT NULL,
    reason TEXT,
    PRIMARY KEY (flight_id, seat_no)
);


-- Задание 3: Посадка в резервном аэропорту и причины
ALTER TABLE flights
ADD COLUMN IF NOT EXISTS actual_arrival_airport CHAR(3) REFERENCES airports_data(airport_code),
ADD COLUMN IF NOT EXISTS divert_reason TEXT;

-- Обновляем представление timetable
CREATE OR REPLACE VIEW timetable AS
SELECT f.flight_id,
    f.route_no,
    r.departure_airport,
    r.arrival_airport,
    f.status,
    r.airplane_code,
    f.scheduled_departure,
    (f.scheduled_departure AT TIME ZONE dep.timezone) AS scheduled_departure_local,
    f.actual_departure,
    (f.actual_departure AT TIME ZONE dep.timezone) AS actual_departure_local,
    f.scheduled_arrival,
    (f.scheduled_arrival AT TIME ZONE arr.timezone) AS scheduled_arrival_local,
    f.actual_arrival,
    -- Учитываем часовой пояс фактического аэропорта, если он изменился, иначе планового
    (f.actual_arrival AT TIME ZONE COALESCE(act_arr.timezone, arr.timezone)) AS actual_arrival_local,
    f.actual_arrival_airport,
    f.divert_reason
FROM flights f
JOIN routes r ON r.route_no = f.route_no AND r.validity @> f.scheduled_departure
JOIN airports_data dep ON dep.airport_code = r.departure_airport
JOIN airports_data arr ON arr.airport_code = r.arrival_airport
LEFT JOIN airports_data act_arr ON act_arr.airport_code = f.actual_arrival_airport;
