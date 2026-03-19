1. Какие ключевые слова возможно использовать внутри оператора INSERT?

- VALUES / DEFAULT VALUES
- OVERRIDING SYSTEM VALUE | OVERRIDING USER VALUE (для столбцов-identity)
- INSERT … SELECT (вместо VALUES — подзапрос)
- ON CONFLICT DO NOTHING | DO UPDATE SET …
- RETURNING …
- WITH … INSERT … (CTE перед INSERT) Примеры:
- INSERT INTO t DEFAULT VALUES;
- INSERT INTO t(a,b) VALUES ($1, DEFAULT) RETURNING id;
- WITH s AS (SELECT …) INSERT INTO t(a,b) SELECT a,b FROM s ON CONFLICT (a) DO UPDATE SET b = EXCLUDED.b;

2. Каким образом возможно обновить сразу несколько значений

- Несколько столбцов сразу: UPDATE t SET col1 = v1, col2 = v2 WHERE …; или кортежем: UPDATE t SET (col1, col2) = (v1, v2) WHERE …;
- Разные значения для разных строк: UPDATE t SET col = CASE id WHEN 1 THEN 10 WHEN 2 THEN 20 END WHERE id IN (1,2);
- По данным из другой таблицы/CTE: UPDATE g SET grade = s.new_grade FROM staging s WHERE g.id = s.id;

3. Возможно ли использовать операции объединения в операторе INSERT? Если да, то пример. Да, через INSERT … SELECT с объединением: INSERT INTO grades(student_id, subject_id, grade) SELECT 1, 2, 5 UNION ALL SELECT 2, 2, 4; (UNION ALL предпочтительнее, если не нужно устранять дубликаты.)
    
4. Возможно ли изменять порядок атрибутов при вводе данных в таблицу? Да. Указывайте явный список столбцов в любом порядке, а значения — в соответствующем порядке: INSERT INTO t(b, a, c) VALUES ($1, $2, DEFAULT); Неуказанные столбцы должны иметь DEFAULT или быть NULL-совместимыми.
    
5. В чем отличие между операторами DELETE и TRUNCATE
    

- DELETE: удаляет выбранные строки (с WHERE), построчно, запускает row-level триггеры, полноценно журналируется; медленнее на больших объёмах; можно вернуть количество строк.
- TRUNCATE: мгновенно очищает всю таблицу (без WHERE), журналируется минимально, не запускает row-level триггеры (есть statement-level ON TRUNCATE), может сбросить счетчик identity/serial (RESTART IDENTITY), требует более сильные блокировки; в PostgreSQL транзакционен (можно откатить).

---
# Task-1

```sql
CREATE TABLE debtor_students
(
 id SERIAL PRIMARY KEY,
 last_name VARCHAR(30) NOT NULL,
 first_name VARCHAR(30) NOT NULL,
 patronymic VARCHAR(30) NULL,
 student_id integer NOT NULL,
 students_group_number VARCHAR(7) NOT NULL,
 debt_number INTEGER NOT NULL
);
-- DROP TABLE debtor_students;
INSERT INTO debtor_students (last_name, first_name, patronymic,
 student_id, students_group_number,
debt_number)
(
 SELECT last_name, first_name, patronymic,
 students.student_id, students_group_number, COUNT(*) AS
"Number of debts"
 FROM students
 INNER JOIN field_comprehensions ON
 field_comprehensions.student_id = students.student_id
 WHERE field_comprehensions.mark = 2
 GROUP BY 1,2,3,4,5
);
UPDATE students s
SET last_name = '!' || s.last_name
FROM debtor_students ds
WHERE debt_number > 12 and s.student_id = ds.student_id;
```

- Создаёт таблицу debtor_students — «снимок» должников: ФИО, id студента, номер группы и количество долгов (debt_number). Поле id — автоинкремент.
    
- Заполняет её через INSERT … SELECT: из таблиц students и field_comprehensions берутся записи с оценкой 2, по каждому студенту считается COUNT(`*`) долгов, и результат вставляется в debtor_students (по одной строке на должника).
    
- Обновляет таблицу students: для тех, у кого в debtor_students debt_number > 12, к фамилии добавляется «!» в начале (UPDATE с JOIN по student_id).
    

Итог: получаете список должников с числом долгов и помечаете «супер‑должников» в основной таблице. Примечание: повторный запуск вставки добавит ещё строки в debtor_students, а обновление добавит ещё один «!» к фамилии.

--- 

# Task-2


```sql
ALTER TABLE students DROP CONSTRAINT chk_inn_format;
UPDATE students s
SET INN = (EXTRACT(YEAR from s.birthday)::bigint * 100000000
 + s.student_id::bigint * 1
UPDATE students s
SET inn = (inn::bigint
 + ( (
 (inn::bigint / 100000000000) % 10 * 7 +
 (inn::bigint / 10000000000 ) % 10 * 2 +
 (inn::bigint / 1000000000 ) % 10 * 4 +
 (inn::bigint / 100000000 ) % 10 * 10 +
 (inn::bigint / 10000000 ) % 10 * 3 +
 (inn::bigint / 1000000 ) % 10 * 5 +
 (inn::bigint / 100000 ) % 10 * 9
(inn::bigint / 10000 ) % 10 * 4 +
 (inn::bigint / 1000 ) % 10 * 6 +
 (inn::bigint / 100 ) % 10 * 8
 ) / 11 ) % 10 * 10)
UPDATE students s
SET inn = (inn::bigint
 + ( (
 (inn::bigint / 100000000000) % 10 * 3 +
 (inn::bigint / 10000000000 ) % 10 * 7 +
 (inn::bigint / 1000000000 ) % 10 * 2 +
 (inn::bigint / 100000000 ) % 10 * 4 +
 (inn::bigint / 10000000 ) % 10 * 10 +
 (inn::bigint / 1000000 ) % 10 * 3 +
 (inn::bigint / 100000 ) % 10 * 5 +
 (inn::bigint / 10000 ) % 10 * 9 +
 (inn::bigint / 1000 ) % 10 * 4 +
 (inn::bigint / 100 ) % 10 * 6 +
 (inn::bigint / 10 ) % 10 * 8
 ) / 11 ) % 10 )::varchar(12);
```

- Удаляет ограничение chk_inn_format на таблице students, чтобы временно разрешить «некорректные» значения INN в процессе перерасчета.
- Пересчитывает INN:
    - Шаг 1: формирует базовую числовую часть ИНН на основе года рождения и student_id.
    - Шаг 2: добавляет первый контрольный разряд по взвешенной сумме цифр (mod 11, затем mod 10), умножая на 10 (чтобы занять предпоследнюю позицию).
	- Шаг 3: добавляет второй контрольный разряд по другой системе весов (mod 11, затем mod 10) и приводит итог к строке длиной 12 символов (varchar(12)).

---

# Task-3

```sql
INSERT INTO sick_leave_list (student_id, certificate_id, since, till)
values
(820611, 1000, '2024-11-05', '2024-11-08'),
(866735, 1001, '2024-11-09', '2024-11-16'),
(829651, 1002, '2024-12-28', '2025-01-01'),
(852471, 1003, '2024-11-21', '2024-11-22'),
(870446, 1004, '2025-01-07', '2025-01-14'),
(819225, 1005, '2025-01-26', '2025-01-28'),
(878202, 1006, '2025-02-11', '2025-02-14'),
(840132, 1007, '2025-02-19', '2025-02-23'),
(863719, 1008, '2025-03-13', '2025-03-16'),
(890704, 1009, '2025-03-21', '2025-03-26');

INSERT INTO doctors (doctor_id, last_name, first_name, patronymic)
values
(7016784, 'Фёдоров', 'Иван', 'Александрович'),
(7040575, 'Петрова', 'Екатерина', 'Алексеевна'),
(7030742, 'Кузнецов', 'Дмитрий', 'Артёмович'),
(7035636, 'Попова', 'Ирина', 'Евгеньевна'),
(7060105, 'Петров', 'Сергей', 'Артёмович'),
(7004102, 'Морозова', 'Ольга', 'Сергеевна'),
(7074455, 'Фёдоров', 'Максим', 'Владимирович'),
(7092651, 'Петрова', 'Елена', 'Владимировна'),
(7007426, 'Соколов', 'Алексей', 'Александрович'),
(7077408, 'Соколова', 'Юлия', 'Владимировна');

INSERT INTO doctor_to_leave_list (doctor_id, certificate_id)
values
(7016784, 1000),
(7040575, 1001),
(7030742, 1002),
(7035636, 1003),
(7060105, 1004),
(7004102, 1005),
(7074455, 1006),
(7092651, 1007),
(7007426, 1008),
(7077408, 1009);

-- TEST
select sll.student_id, s.last_name, s.first_name, since, till,
       ds.doctor_id, ds.last_name, ds.first_name, ds.patronymic
from sick_leave_list sll
join doctor_to_leave_list dtll on sll.certificate_id = dtll.certificate_id
join doctors ds on ds.doctor_id = dtll.doctor_id
join students s on s.student_id = sll.student_id;
```

- Вставляет записи о больничных студентов в таблицу sick_leave_list: student_id, номер справки (certificate_id), даты since/till.
- Вставляет справочник врачей в таблицу doctors: doctor_id и ФИО.
- Заполняет таблицу-связку doctor_to_leave_list, которая привязывает врача к конкретной справке (certificate_id).
- Тестовый запрос выводит сводную выборку: студент, период больничного и назначенный врач, объединяя все три таблицы и таблицу students по ключам.