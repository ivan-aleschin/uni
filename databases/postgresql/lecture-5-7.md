
# PostgreSQL — конспект по основным командам (по лабам 5–7)

## DML: вставка/обновление/удаление

- INSERT INTO — вставка строк.
  - Варианты источника:
    - VALUES (...), (...), ...
    - DEFAULT VALUES (все колонки берут DEFAULT/NULL)
    - INSERT ... SELECT ... (вставка результата запроса; можно с UNION/CTE)
  - Обработка конфликтов: ON CONFLICT (колонки | ON CONSTRAINT имя) DO NOTHING | DO UPDATE SET ...
  - Возврат значений: RETURNING id, ... (возвращает вставленные/обновлённые строки)
  - Примеры:
    - INSERT INTO t DEFAULT VALUES RETURNING id;
    - INSERT INTO t(a,b) VALUES ($1, DEFAULT) RETURNING id;
    - WITH src AS (SELECT ...) INSERT INTO t(a,b) SELECT a,b FROM src ON CONFLICT (a) DO UPDATE SET b = EXCLUDED.b;

- UPDATE ... SET ... — изменение строк.
  - С JOIN: UPDATE tgt SET ... FROM other WHERE tgt.key = other.key AND ...
  - Пример: UPDATE students s SET last_name = '!' || s.last_name FROM debtor_students ds WHERE s.student_id = ds.student_id AND ds.debt_number > 12;

- DELETE vs TRUNCATE
  - DELETE — построчно, можно с WHERE, запускает row-триггеры, полно журналируется.
  - TRUNCATE — быстро очистить всю таблицу, без WHERE, можно RESTART IDENTITY, не вызывает row-триггеры, транзакционен в PostgreSQL.

## SELECT и агрегации

- JOIN ... ON ... — соединения таблиц по ключам (INNER/LEFT и т. д.).
- GROUP BY — группировка для агрегатов (COUNT/AVG/...). Лучше явно перечислять колонки, чем позиционно GROUP BY 1,2,3.
- Регулярные выражения:
  - ~  — чувствительно к регистру; ~* — нечувствительно.
  - Пример: field_name ~* '.*баз.*данных.*'
- Сортировка и фильтры:
  - ORDER BY col [ASC|DESC]
  - WHERE ... (использует индексы при равенстве/диапазонах; регэкспы и функции на колонке часто мешают индексам)

## Транзакции и уровни изоляции

- BEGIN [ISOLATION LEVEL Read Committed | Repeatable Read | Serializable];
- COMMIT / ROLLBACK.
- Видимость (PostgreSQL):
  - Read Uncommitted = Read Committed.
  - Read Committed — видит коммиты других транзакций, сделанные до выполнения текущего запроса.
  - Repeatable Read/Serializable — «снимок» на момент начала транзакции (последующие внешние коммиты внутри неё не видны).

## Индексы и производительность

- CREATE INDEX ON table (column [ASC|DESC]);
  - Ускоряют равенство/диапазоны/JOIN по этому столбцу и могут помочь в ORDER BY.
  - Цена: место + доп. работа при INSERT/UPDATE/DELETE.
- Примеры:
  - CREATE INDEX ON field_comprehensions (student_id);
  - CREATE INDEX ON attendance (generated_code);
- Замечания:
  - Регулярные выражения и функции в WHERE/ORDER BY часто не используют обычный B‑Tree индекс.
  - Для равенства/сортировки строк B-Tree подходит; для полнотекстового — GIN/GiST.

## CTE (WITH)

- WITH имя AS (SELECT ...) INSERT/UPDATE/SELECT ...
  - Удобно подготовить данные и использовать их в одном операторе.
  - Пример: WITH s AS (SELECT ...) INSERT INTO t SELECT ... FROM s RETURNING id;

## PL/pgSQL: DO-блоки, триггеры, процедуры, функции

- DO $$ ... $$ — анонимный блок PL/pgSQL.
  - Объявление переменных: DECLARE var int := 0;
  - Цикл по результату: FOR r IN SELECT ... LOOP ... END LOOP;
  - Условия: IF ... ELSIF ... ELSE ... END IF;
  - Сообщения: RAISE NOTICE 'msg %', value;

- Триггеры:
  - Функция-триггер: CREATE OR REPLACE FUNCTION f() RETURNS TRIGGER LANGUAGE plpgsql AS $$ BEGIN ... RETURN NEW; END; $$;
  - Создание триггера: CREATE TRIGGER trg AFTER INSERT|UPDATE ON table FOR EACH ROW EXECUTE FUNCTION f();
  - Пример уведомления при вставке в sick_leave_list: RAISE NOTICE '% has left sick', NEW.student_id;

- Функции (LANGUAGE SQL/PLPGSQL):
  - SQL-функция может возвращать скаляр/таблицу (RETURNS TABLE ...).
  - Используется для инкапсуляции запросов (например, вычисление моды по оценкам).

- Процедуры (CREATE PROCEDURE ... LANGUAGE SQL/PLPGSQL; CALL ...):
  - Можно выполнять внутри управление транзакциями.
  - Пример: повышение оценки на день рождения по выбранной дисциплине.

## Генерация данных и полезные функции

- random(), md5(text), to_timestamp(epoch), extract(epoch from ts), интервал '1 SECOND'::interval.
- Пример генерации миллиона записей с датами/случайными студентами:
  - md5(random()::text) как код,
  - enter_time между '2023-01-01' и '2023-12-31',
  - exit_time = enter_time + случайная продолжительность.

## DDL: создание и изменение схемы

- CREATE TABLE ... (id SERIAL PRIMARY KEY, ..., FOREIGN KEY (...) REFERENCES ...);
- ALTER TABLE ... DROP CONSTRAINT имя; — временно снять ограничение (например, для перерасчёта инвариантов).
- Внешние ключи: FOREIGN KEY (person_id) REFERENCES student_ids(student_id).

## Типичные подводные камни

- Повторные INSERT ... SELECT без уникальных ограничений → дубликаты «снимков» (решение: TRUNCATE перед перезаливкой или ON CONFLICT).
- UPDATE, добавляющий префикс (например, '!') — неидемпотентен (при повторе добавит ещё один '!').
- Регэкспы и функции в WHERE мешают использованию индексов; по возможности фильтруйте по индексируемым предикатам.