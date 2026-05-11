#!/usr/bin/env python3
"""
Лабораторная работа 8: Улучшенное приложение бронирования.
Добавлена отмена бронирований (cancel_booking), детали рейса (get_flight_info).
Зависимости: psycopg2 — объявлен в pyproject.toml, предоставляется через flake.nix.
Запуск (из корня репозитория): nix develop && python3 databases/pgcli/lab-8/app.py
"""
import sys
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'demo',
    'user': 'postgres',
    'options': '-c search_path=bookings -c bookings.lang=ru',
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def print_header(title: str):
    line = "─" * (len(title) + 4)
    print(f"\n┌{line}┐")
    print(f"│  {title}  │")
    print(f"└{line}┘")


def show_available_flights():
    print_header("Доступные рейсы")
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT
                f.flight_id,
                f.route_no,
                r.departure_airport                            AS dep,
                r.arrival_airport                             AS arr,
                (dep_ap.city ->> 'ru')                        AS dep_city,
                (arr_ap.city ->> 'ru')                        AS arr_city,
                (f.scheduled_departure AT TIME ZONE dep_ap.timezone)::timestamp AS dep_local,
                f.status,
                check_free_seats(f.flight_id)                 AS free_seats
            FROM flights f
            JOIN routes r ON r.route_no = f.route_no
                AND r.validity @> f.scheduled_departure
            JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
            JOIN airports_data arr_ap ON arr_ap.airport_code = r.arrival_airport
            WHERE f.status IN ('Scheduled', 'On Time')
              AND check_free_seats(f.flight_id) > 0
            ORDER BY f.scheduled_departure
            LIMIT 20
        """)
        rows = cur.fetchall()

    if not rows:
        print("  Нет доступных рейсов.")
        return

    fmt = "{:>8}  {:<10}  {:<20}  →  {:<20}  {:<20}  {:<12}  {:>4}"
    print(fmt.format("ID", "Маршрут", "Откуда (город)", "Куда (город)", "Вылет (местное)", "Статус", "Мест"))
    print("─" * 110)
    for r in rows:
        dep_city = f"{r['dep_city']} ({r['dep']})"
        arr_city = f"{r['arr_city']} ({r['arr']})"
        print(fmt.format(
            r['flight_id'], r['route_no'],
            dep_city[:20], arr_city[:20],
            str(r['dep_local'])[:16],
            r['status'], r['free_seats'],
        ))


def show_flight_details():
    try:
        flight_id = int(input("\nID рейса: ").strip())
    except ValueError:
        print("Ошибка: введите числовой ID.")
        return

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM get_flight_info(%s)", (flight_id,))
        row = cur.fetchone()

    if not row:
        print(f"  Рейс {flight_id} не найден.")
        return

    print(f"\n  Рейс          : {row['flight_id']} ({row['route_no']})")
    print(f"  Маршрут       : {row['dep_city']} ({row['departure_airport']}) → {row['arr_city']} ({row['arrival_airport']})")
    print(f"  Вылет (UTC)   : {str(row['scheduled_dep'])[:19]}")
    print(f"  Вылет (местн.): {str(row['dep_local'])[:19]}")
    print(f"  Статус        : {row['status']}")
    print(f"  Мест всего    : {row['total_seats']}")
    print(f"  Продано       : {row['sold_seats']}")
    print(f"  Свободно      : {row['free_seats']}")


def book_ticket_interactive():
    print_header("Новое бронирование")
    show_available_flights()

    try:
        flight_id = int(input("\nID рейса: ").strip())
    except ValueError:
        print("Ошибка: введите числовой ID.")
        return

    passenger_id = input("ID документа (например: RU 1234567890123): ").strip()
    if not passenger_id:
        print("Ошибка: ID пассажира не может быть пустым.")
        return

    passenger_name = input("Имя (латиница, например: Ivan Petrov): ").strip()
    if not passenger_name:
        print("Ошибка: имя пассажира не может быть пустым.")
        return

    print("  1 — Economy\n  2 — Comfort\n  3 — Business")
    fare_map = {'1': 'Economy', '2': 'Comfort', '3': 'Business'}
    fare_conditions = fare_map.get(input("Класс [1/2/3]: ").strip())
    if fare_conditions is None:
        print("Ошибка: введите 1, 2 или 3.")
        return

    try:
        price = float(input(f"Цена ({fare_conditions}), руб.: ").strip())
    except ValueError:
        print("Ошибка: введите числовую цену.")
        return

    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                "SELECT book_ticket(%s, %s, %s, %s, %s)",
                (passenger_id, passenger_name, flight_id, fare_conditions, price),
            )
            book_ref = cur.fetchone()[0]
            conn.commit()
            print(f"\n  ✓ Бронирование создано!")
            print(f"    Номер бронирования : {book_ref}")
            print(f"    Пассажир           : {passenger_name}")
            print(f"    Рейс / Класс / Цена: {flight_id} / {fare_conditions} / {price:.2f} руб.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"\n  ✗ Ошибка: {(e.pgerror or str(e)).strip()}")


def cancel_booking_interactive():
    print_header("Отмена бронирования")
    book_ref = input("Номер бронирования: ").strip().upper()
    if not book_ref:
        return

    confirm = input(f"Вы уверены, что хотите отменить бронирование {book_ref}? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("  Отмена не выполнена.")
        return

    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute("SELECT cancel_booking(%s)", (book_ref,))
            conn.commit()
            print(f"  ✓ Бронирование {book_ref} успешно отменено.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"  ✗ Ошибка: {(e.pgerror or str(e)).strip()}")


def show_booking():
    print_header("Информация о бронировании")
    book_ref = input("Номер бронирования: ").strip().upper()
    if not book_ref:
        return

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT
                b.book_ref,
                (b.book_date AT TIME ZONE 'Europe/Moscow')::timestamp AS book_date,
                b.total_amount,
                t.passenger_name,
                t.ticket_no,
                s.flight_id,
                s.fare_conditions,
                s.price,
                f.route_no,
                f.status,
                r.departure_airport AS dep,
                r.arrival_airport   AS arr,
                (dep_ap.city ->> 'ru') AS dep_city,
                (arr_ap.city ->> 'ru') AS arr_city,
                (f.scheduled_departure AT TIME ZONE dep_ap.timezone)::timestamp AS dep_local
            FROM bookings b
            JOIN tickets t ON t.book_ref = b.book_ref
            JOIN segments s ON s.ticket_no = t.ticket_no
            JOIN flights f ON f.flight_id = s.flight_id
            JOIN routes r ON r.route_no = f.route_no
                AND r.validity @> f.scheduled_departure
            JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
            JOIN airports_data arr_ap ON arr_ap.airport_code = r.arrival_airport
            WHERE b.book_ref = %s
            ORDER BY s.flight_id
        """, (book_ref,))
        rows = cur.fetchall()

    if not rows:
        print(f"  Бронирование «{book_ref}» не найдено.")
        return

    print(f"\n  Бронирование : {rows[0]['book_ref']}")
    print(f"  Создано      : {str(rows[0]['book_date'])[:19]}")
    print(f"  Пассажир     : {rows[0]['passenger_name']}")
    print()
    for row in rows:
        print(f"  Билет {row['ticket_no']}:")
        print(f"    Рейс   : {row['flight_id']} ({row['route_no']})  {row['dep_city']} ({row['dep']}) → {row['arr_city']} ({row['arr']})")
        print(f"    Вылет  : {str(row['dep_local'])[:16]}   Статус: {row['status']}")
        print(f"    Класс  : {row['fare_conditions']} / {row['price']:.2f} руб.")


def main():
    print("╔════════════════════════════════════════════════╗")
    print("║   Система бронирования авиабилетов  (v2.0)    ║")
    print("║   БД: demo (PostgresPro) · Лаб. работа 8     ║")
    print("╚════════════════════════════════════════════════╝")

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT version()")
            print(f"  Подключено: {cur.fetchone()[0]}")
    except psycopg2.OperationalError as e:
        print(f"Не удалось подключиться к БД: {e}")
        sys.exit(1)

    while True:
        print("\n  1 — Доступные рейсы")
        print("  2 — Детали рейса")
        print("  3 — Забронировать билет")
        print("  4 — Информация о бронировании")
        print("  5 — Отменить бронирование")
        print("  0 — Выход")

        choice = input("\nДействие: ").strip()

        if choice == '0':
            print("До свидания!")
            break
        elif choice == '1':
            show_available_flights()
        elif choice == '2':
            show_flight_details()
        elif choice == '3':
            book_ticket_interactive()
        elif choice == '4':
            show_booking()
        elif choice == '5':
            cancel_booking_interactive()
        else:
            print("  Неверный выбор. Введите 0–5.")


if __name__ == '__main__':
    main()
