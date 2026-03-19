1. За счет чего индексы ускоряют выборку данных?

- Структуры (чаще всего B-деревья) позволяют логарифмический поиск по ключу и использовать порядок для диапазонов и сортировок.
- Снижают объём читаемых страниц; возможен Index Only Scan (чтение лишь индекса при валидной visibility map).
- Поддерживают выборки по выражениям/частям данных (expression/partial indexes).

2. Существуют ли случаи, когда использование индексов замедляет выборку данных? Да:

- Низкая селективность (запрос возвращает большую долю таблицы) — последовательное сканирование быстрее, чем случайные чтения по индексу.
- Очень маленькие таблицы — дешевле прочитать целиком.
- Неподходящий тип индекса под условие/оператор (например, B-Tree для полнотекстового поиска).
- Ошибочный выбор плана (неактуальная статистика) может привести к ухудшению.

3. Какая структура данных хранит в себе индексные записи?

- По умолчанию: B-Tree (вариант B+Tree).
- Также есть: Hash, GiST, SP-GiST, GIN, BRIN — под разные типы запросов/данных.

4. Для чего предназначены транзакции?

- Группировка операций с гарантиями ACID:
    - Atomicity — всё или ничего,
    - Consistency — сохранение инвариантов,
    - Isolation — изоляция параллельных транзакций,
    - Durability — сохранность после фиксации.
- Управление конкурентным доступом и согласованностью данных.

5. В чем отличие между неповторяющимся и фантомным чтением?

- Неповторяющееся чтение (non-repeatable read): одно и то же условие/строка, прочитанная дважды, даёт разные значения из-за UPDATE/DELETE параллельной транзакции.
- Фантомное чтение (phantom read): между двумя одинаковыми запросами появляются/исчезают новые строки, удовлетворяющие условию, из-за INSERT/DELETE параллельной транзакции. Примечание для PostgreSQL: уровень REPEATABLE READ использует snapshot isolation и предотвращает оба эффекта для видимости данных, но возможны сериализационные конфликты; уровень SERIALIZABLE дополнительно предотвращает сериализационные аномалии.

---

# Task-1

```sql
CREATE TABLE attendance (
  attendance_id SERIAL PRIMARY KEY,
  generated_code varchar(64),
  person_id integer,
  enter_time timestamp,
  exit_time timestamp,
  FOREIGN KEY (person_id) REFERENCES student_ids (student_id)
);

do
$$
DECLARE
  enter_time timestamp(0);
  exit_time timestamp(0);
  person_id integer;
  enter_id varchar(64);
BEGIN
  FOR i IN 1..1000000 LOOP
    --raise notice '%', i;
    enter_time := to_timestamp(random() *
      (
        extract(epoch from '2023-12-
31'::date) -
        extract(epoch from '2023-01-
01'::date)
      )
      + extract(epoch from '2023-01-
01'::date)
    );

    exit_time := enter_time + (floor(random() * 36000 + 1) * '1
SECOND'::interval);

    person_id := (
      SELECT student_id FROM students
      ORDER BY random()
      LIMIT 1
    );

    enter_id := md5(random()::text);

    INSERT INTO attendance (generated_code, person_id, enter_time, exit_time)
    VALUES (enter_id, person_id, enter_time, exit_time);
  END LOOP;
END
$$;

do
$$
DECLARE
  enter_time timestamp(0);
  exit_time timestamp(0);
  person_id integer;
  enter_id varchar(64);
BEGIN
  enter_time := to_timestamp(random() *
    (
      extract(epoch from '2023-12-
31'::date) -
      extract(epoch from '2023-01-
01'::date)
    )
    + extract(epoch from '2023-01-
01'::date)
  );

  exit_time := enter_time + (floor(random() * 36000 + 1) * '1
SECOND'::interval);

  person_id := (
    SELECT student_id FROM students
    ORDER BY random()
    LIMIT 1
  );

  enter_id := md5(random()::text);

  raise notice '% | % | % | %', enter_id, person_id, enter_time, exit_time;

  -- INSERT INTO attendance (generated_code, person_id, enter_time, exit_time)
  -- VALUES (enter_id, person_id, enter_time, exit_time);
END
$$;

CREATE INDEX ON attendance (generated_code ASC);

-- 2.1.1. ---------------------------------------------------------------
-- | Time before INDEXing Tb | Time after INDEXing Ta | Ta / Tb |
-- SELECT | 2423,985 ms (00:02,424) | 1906,206 ms (00:01,906) | ~0,786 |
-- INSERT | 200,793 ms | 3,891 ms | ~0,019 |
-------------------------------------------------------------------------

select student_id from students order by random() limit 1;

CREATE INDEX ON attendance (person_id);

-- 2.1.2. ---------------------------------------------------------------
-- | Time before INDEXing Tb | Time after INDEXing Ta | Ta / Tb |
-- SELECT | 1906,206 ms (00:01,906) | 1786,255 ms (00:01,786) | ~0,937 |
-- SELECT | | | |
-- +WHERE | 59,566 ms | 18,51 ms | ~0,311 |
-------------------------------------------------------------------------

-- 2.1.3.
select *
from attendance
where generated_code ~ '.*a$'
order by generated_code;

-- without order by ~ 0.8 secs
-- with order by ~ 0.5 secs
```

- Создаёт таблицу attendance для фиксации посещений: сгенерированный код входа, id студента, время входа/выхода, внешний ключ на student_ids.student_id.
- Генерирует тестовые данные:
  - DO-блок №1: вставляет 1 000 000 записей со случайными датами в 2023 году, случайной продолжительностью сеанса (до 10 часов), случайным студентом и псевдо-уникальным кодом md5(random()).
  - DO-блок №2: генерирует одну запись и выводит её в NOTICE (вставка закомментирована) — для наглядной проверки.
- Индексация:
  - Создаёт индекс по generated_code для ускорения поиска и сортировки по коду.
  - Создаёт индекс по person_id для ускорения фильтрации по студенту.
  - Приведены замеры времени до/после индексации (SELECT/INSERT).
- Проверочные запросы:
  - Случайный student_id из students.
  - Поиск записей attendance с regex-фильтром по окончанию кода на «a» и сортировкой по generated_code, с комментариями по времени выполнения.

---

# Task-2

```sql
select * from students
where student_id= 873305;

select field_name, mark, semester from field_comprehensions
JOIN fields ON field = field_id
where student_id = 873305
order by 3;

BEGIN ISOLATION LEVEL Serializable; --Repeatable read; --Read committed;
select field_name, mark, semester from field_comprehensions
JOIN fields ON field = field_id
where student_id = 873305
and (field_name ~* '.*опер.*систем.*'
 or field_name ~* '.*баз.*данных.*'
 )
order by 3;
ROLLBACK;

-- Профессора:
select * from students
where student_id= 873305;

select field_name, mark, semester, field from field_comprehensions
JOIN fields ON field = field_id
where student_id = 873305
 and (field_name ~* '.*опер.*систем.*'
 or field_name ~* '.*баз.*данных.*'
 )
order by 3;

BEGIN;
UPDATE field_comprehensions
SET mark = 2
FROM fields
WHERE field = field_id
 AND student_id = 873305
 and (field_name ~* '.*опер.*систем.*'
 or field_name ~* '.*баз.*данных.*'
 );
COMMIT;
--ROLLBACK;

BEGIN ISOLATION LEVEL Serializable;--Repeatable read; --Read committed;
UPDATE field_comprehensions
SET mark = 5
FROM fields
WHERE field = field_id
 AND student_id = 873305
 and (field_name ~* '.*опер.*систем.*'
 or field_name ~* '.*баз.*данных.*'
 );
COMMIT;

-- Isolation Level | Before Commitment | After Commitment
-- Read uncommitted | 2, 2 | 5, 5
-- Read committed   | 2, 2 | 5, 5
-- Repeatable Read  | 2, 2 | 2, 2
-- Serializable     | 2, 2 | 2, 2
```

- Блок 1 (студенты): показывает исходные данные по студенту 873305; в рамках транзакции с заданным уровнем изоляции выполняет выборку оценок по предметам, подходящим под регулярные выражения (операционные системы/базы данных), затем ROLLBACK. Это демонстрация «снимка» видимости при разном уровне изоляции.
- Блок 2 (профессора): 
  - Сначала фиксирует оценки в 2 балла по выбранным предметам для студента 873305 и фиксирует транзакцию (COMMIT).
  - Затем в новой транзакции (c заданным уровнем изоляции) обновляет оценки до 5 и фиксирует.
  - Сравнение видимости/поведения в разных уровнях изоляции:
    - Read committed: после коммита «видно» новые значения в последующих запросах/транзакциях.
    - Repeatable Read/Serializable: внутри одной транзакции сохраняется «снимок» — уже после начала транзакции новые коммиты извне не видны до её завершения.
    - Примечание для PostgreSQL: Read uncommitted эквивалентен Read committed.

Подписи автора в коде фиксируют ожидаемые результаты:
- Read uncommitted | 2, 2 | 5, 5
- Read committed   | 2, 2 | 5, 5
- Repeatable Read  | 2, 2 | 2, 2
- Serializable     | 2, 2 | 2, 2

---

# Task-3

```sql
CREATE INDEX ON field_comprehensions (student_id ASC);
```

- Цель: ускорить выборку оценок одного конкретного студента из таблицы field_comprehensions (около 25 000 записей).
- Решение: создать индекс по столбцу student_id. Это ускоряет запросы вида:
  - WHERE student_id = ?
  - JOIN по student_id
  - Потенциально упрощает ORDER BY student_id
- Побочные эффекты: небольшой расход доп. места и замедление операций INSERT/UPDATE/DELETE на эту таблицу из‑за поддержки индекса.
Итог: потому что порой среди множества студентов нам нужны оценки лишь одного. А оценок всего порядка 25000, поэтому поиск по данной таблице затруднён. Данный индекс ускоряет поиск оценок каждого отдельного студента.