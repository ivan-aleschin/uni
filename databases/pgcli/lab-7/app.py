#!/usr/bin/env python3
"""
Лабораторная работа 7: Приложение бронирования авиабилетов.
Использует хранимые процедуры из Лабораторной работы 5 (book_ticket, check_free_seats).
Зависимости: psycopg2 — объявлен в pyproject.toml, предоставляется через flake.nix.
Запуск (из корня репозитория): nix develop && python3 databases/pgcli/lab-7/app.py
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


def show_available_flights():
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT
                f.flight_id,
                f.route_no,
                r.departure_airport AS dep,
                r.arrival_airport   AS arr,
                (f.scheduled_departure AT TIME ZONE dep_ap.timezone)::timestamp AS dep_local,
                f.status,
                check_free_seats(f.flight_id) AS free_seats
            FROM flights f
            JOIN routes r ON r.route_no = f.route_no
                AND r.validity @> f.scheduled_departure
            JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
            WHERE f.status IN ('Scheduled', 'On Time')
              AND check_free_seats(f.flight_id) > 0
            ORDER BY f.scheduled_departure
            LIMIT 20
        """)
        rows = cur.fetchall()
        if not rows:
            print("Нет доступных рейсов.")
            return
        print()
        print(f"{'ID':>8}  {'Маршрут':<10}  {'Откуда':>6} → {'Куда':<6}  {'Вылет (местное)':<20}  {'Статус':<12}  {'Свободных мест'}")
        print("─" * 90)
        for r in rows:
            dep_str = str(r['dep_local'])[:16]
            print(f"{r['flight_id']:>8}  {r['route_no']:<10}  {r['dep']:>6} → {r['arr']:<6}  {dep_str:<20}  {r['status']:<12}  {r['free_seats']}")


def book_ticket_interactive():
    print("\n╔══════════════════════════════╗")
    print("║  Новое бронирование          ║")
    print("╚══════════════════════════════╝")

    show_available_flights()

    try:
        flight_id = int(input("\nID рейса: ").strip())
    except ValueError:
        print("Ошибка: введите числовой ID.")
        return

    passenger_id = input("ID документа пассажира (например: RU 1234567890123): ").strip()
    if not passenger_id:
        print("Ошибка: ID пассажира не может быть пустым.")
        return

    passenger_name = input("Имя пассажира (латиница, например: Ivan Petrov): ").strip()
    if not passenger_name:
        print("Ошибка: имя пассажира не может быть пустым.")
        return

    print("Классы обслуживания:")
    print("  1 — Economy")
    print("  2 — Comfort")
    print("  3 — Business")
    fare_choice = input("Выберите класс [1/2/3]: ").strip()
    fare_map = {'1': 'Economy', '2': 'Comfort', '3': 'Business'}
    fare_conditions = fare_map.get(fare_choice)
    if fare_conditions is None:
        print("Ошибка: введите 1, 2 или 3.")
        return

    try:
        price = float(input(f"Цена билета ({fare_conditions}), руб.: ").strip())
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
            print(f"\n✓ Бронирование создано!")
            print(f"  Номер бронирования : {book_ref}")
            print(f"  Пассажир           : {passenger_name}")
            print(f"  Рейс               : {flight_id}")
            print(f"  Класс / Цена       : {fare_conditions} / {price:.2f} руб.")
        except psycopg2.Error as e:
            conn.rollback()
            # pgerror содержит человекочитаемое сообщение об ошибке от PostgreSQL
            msg = (e.pgerror or str(e)).strip()
            print(f"\n✗ Ошибка при бронировании:\n  {msg}")


def show_booking():
    book_ref = input("\nНомер бронирования: ").strip().upper()
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
                (f.scheduled_departure AT TIME ZONE dep_ap.timezone)::timestamp AS dep_local,
                r.departure_airport AS dep,
                r.arrival_airport   AS arr
            FROM bookings b
            JOIN tickets t ON t.book_ref = b.book_ref
            JOIN segments s ON s.ticket_no = t.ticket_no
            JOIN flights f ON f.flight_id = s.flight_id
            JOIN routes r ON r.route_no = f.route_no
                AND r.validity @> f.scheduled_departure
            JOIN airports_data dep_ap ON dep_ap.airport_code = r.departure_airport
            WHERE b.book_ref = %s
            ORDER BY s.flight_id
        """, (book_ref,))
        rows = cur.fetchall()

    if not rows:
        print(f"  Бронирование «{book_ref}» не найдено.")
        return

    print(f"\n  Бронирование   : {rows[0]['book_ref']}")
    print(f"  Дата создания  : {str(rows[0]['book_date'])[:19]}")
    print(f"  Пассажир       : {rows[0]['passenger_name']}")
    print()
    for row in rows:
        print(f"  Билет {row['ticket_no']}:")
        print(f"    Рейс        : {row['flight_id']} ({row['route_no']})  {row['dep']} → {row['arr']}")
        print(f"    Вылет       : {str(row['dep_local'])[:16]}   Статус: {row['status']}")
        print(f"    Класс/Цена  : {row['fare_conditions']} / {row['price']:.2f} руб.")


def main():
    print("╔═══════════════════════════════════════════╗")
    print("║   Система бронирования авиабилетов        ║")
    print("║   БД: demo (PostgresPro)                  ║")
    print("╚═══════════════════════════════════════════╝")

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT version()")
            ver = cur.fetchone()[0]
        print(f"  Подключено к: {ver}")
    except psycopg2.OperationalError as e:
        print(f"Не удалось подключиться к БД: {e}")
        sys.exit(1)

    while True:
        print("\n┌─────────────────────────────┐")
        print("│  Меню                       │")
        print("│  1 — Доступные рейсы        │")
        print("│  2 — Забронировать билет     │")
        print("│  3 — Найти бронирование      │")
        print("│  0 — Выход                   │")
        print("└─────────────────────────────┘")

        choice = input("Действие: ").strip()

        if choice == '0':
            print("До свидания!")
            break
        elif choice == '1':
            show_available_flights()
        elif choice == '2':
            book_ticket_interactive()
        elif choice == '3':
            show_booking()
        else:
            print("Неверный выбор. Введите 0–3.")


if __name__ == '__main__':
    main()
