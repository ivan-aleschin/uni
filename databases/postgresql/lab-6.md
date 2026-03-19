1. В чем отличие между процедурой и функцией?

- Функция (CREATE FUNCTION): возвращает значение/набор значений, может использоваться в SQL-выражениях (SELECT, WHERE и т.д.), не может выполнять COMMIT/ROLLBACK внутри; имеет свойства VOLATILE/STABLE/IMMUTABLE, STRICT и т.п.
- Процедура (CREATE PROCEDURE): вызывается через CALL, не возвращает значение как часть запроса, может выполнять управление транзакциями (BEGIN/COMMIT/ROLLBACK) внутри тела.

2. Что такое курсоры? Серверные объекты для пошаговой выборки результата запроса. Позволяют:

- обрабатывать большие наборы данных порциями (FETCH NEXT n),
- выполнять скроллинг (SCROLL/NO SCROLL),
- уменьшать потребление памяти на клиенте. В PostgreSQL: DECLARE c CURSOR FOR SELECT …; затем FETCH/ MOVE/ CLOSE.

3. Для каких целей используют триггеры?

- Автоматическая реакция на события (INSERT/UPDATE/DELETE/TRUNCATE).
- Поддержание сложных инвариантов, аудит (журналы изменений), денормализация/синхронизация агрегатов.
- Валидация данных до записи (BEFORE), логирование/реакции после (AFTER).
- Строковые и операторные триггеры; есть переходные таблицы (REFERENCING NEW/OLD TABLE) для statement-триггеров.

4. Возможно ли написать триггерную функцию на языке SQL? В чистом LANGUAGE SQL — нет (она не имеет доступа к контексту TG_*, NEW/OLD). В PostgreSQL триггерные функции обычно пишут на PL/pgSQL, PL/Python, PL/Perl или на C.
    
5. Для чего нужны представления?
    

- Инкапсуляция сложных запросов и повторное использование.
- Безопасность: выдаём права на VIEW, не на базовые таблицы; маскирование столбцов.
- Стабильный контракт для приложений; можно менять физическую схему без правки кода.
- Производительность: для тяжёлых агрегаций — материальные представления (REFRESH MATERIALIZED VIEW).

---

# Task-1

```sql
SELECT student_id FROM students ORDER BY random() LIMIT 1;

SELECT student_id, AVG(mark)
FROM field_comprehensions
WHERE student_id = 853801
GROUP BY 1;

do
$$
DECLARE
  mark_ptr int;
  sid int := 853801;
  var float := 0;
  amount int := 0;
BEGIN
  --SELECT student_id INTO sid FROM students
  --ORDER BY random() LIMIT 1;

  FOR mark_ptr IN
    SELECT mark
    FROM field_comprehensions
    WHERE student_id = sid
  loop
    if mark_ptr IS NOT NULL then
      var = var + mark_ptr;
      amount = amount + 1;
    end if;
  end loop;

  raise notice '% AVG mark : %/% = %', sid, var, amount, var/amount;
END
$$;
```

- Случайно выбирает одного студента: SELECT student_id FROM students ORDER BY random() LIMIT 1.
- Считает средний балл для конкретного студента (id = 853801) агрегатным запросом AVG(mark) с GROUP BY.
- Блок DO на PL/pgSQL: объявляет переменные, перебирает все оценки выбранного студента, суммирует только не-NULL, считает количество и выводит NOTICE с посчитанным средним. В коде sid зафиксирован как 853801; строка с выбором случайного студента закомментирована.

---

# Task-2

*6*
```sql
do
$$
DECLARE
stud record;
pp int := 0;
BEGIN
for stud in SELECT last_name, first_name, patronymic
FROM students
loop
pp = pp + 1;
if stud.patronymic ~ '.*на$' or stud.last_name ~ '.*а$' then
raise notice '%) ФИО - % % % | Пол - Ж',
pp, stud.last_name, stud.first_name, stud.patronymic;
else
raise notice '%) ФИО - % % % | Пол - М',
pp, stud.last_name, stud.first_name, stud.patronymic;
end if;
end loop;
END
$$;
```

- Перебирает всех студентов.
- Счётчик pp увеличивается на каждой итерации.
- Если отчество оканчивается на “на” или фамилия на “а” — выводит пол «Ж», иначе «М».

*16*

```sql
do
$$
DECLARE
x int;
y int; --random() * 180 - 90;
stud record;
BEGIN
for stud in SELECT student_id FROM students
loop
x = random() * 180 - 90;
y = random() * 180 - 90;
if (x between 1 and 77) and (y between -9 and 67) then
raise notice '% - Европа', stud.student_id;
elsif (x between -34 and 37) and (y between -13 and 51) then
raise notice '% - Африка', stud.student_id;
elsif (x between -39 and -10) and (y between 113 and 153) then
raise notice '% - Австралия', stud.student_id;
elsif (x between 7 and 71) and (y between -168 and -55) then
raise notice '% - Северная Америка', stud.student_id;
elsif (x between -53 and 12) and (y between -81 and -34) then
raise notice '% - Южная Америка', stud.student_id;
elsif x < -63 then
raise notice '% - Антарктида', stud.student_id;
else
raise notice '% - Утонул', stud.student_id;
end if;
end loop;
END
$$;
```

- Для каждого студента генерирует случайные x, y в диапазоне примерно [-90, 90] (формула random() * 180 - 90).
- По диапазонам широт/долгот определяет континент и печатает результат; иначе «Утонул».

*26*

```sql
CREATE PROCEDURE birthday_bonus(param_field varchar(100))
LANGUAGE SQL
AS
$$
UPDATE field_comprehensions SET mark = mark + 1
FROM students, fields
WHERE students.student_id = field_comprehensions.student_id
 AND field_comprehensions.field = fields.field_id
 AND field_name = param_field
 AND mark < 5
 AND EXTRACT(day from current_date) = EXTRACT(day from
students.birthday)
AND EXTRACT(month from current_date) = EXTRACT(month from
students.birthday)
$$;
CALL birthday_bonus('WEB-дизайн');
select * from students
where EXTRACT(day from current_date) = EXTRACT(day from
students.birthday)
 AND EXTRACT(month from current_date) = EXTRACT(month from
students.birthday)
-- 865571
select student_id, field_name, mark from field_comprehensions
JOIN fields on field_id = field
where student_id = 865571 and field_name = 'WEB-дизайн'; -- mark < 5 order
by mark desc
```

- Процедура увеличивает оценку на 1 (но не выше 5) по заданному названию дисциплины в день рождения студента.
- Вызов для WEB-дизайн и проверки выборками.

*36*

```sql
CREATE OR REPLACE FUNCTION temp_smc(s_id integer) RETURNS TABLE (mark
integer, n integer)
LANGUAGE SQL
AS $$
SELECT mark, n
FROM (
SELECT student_id, mark, count(*) as n
FROM field_comprehensions
GROUP BY 1, 2
ORDER BY 1, 2 DESC
) as foo (student_id, mark, n)
WHERE student_id = s_id;
$$;
CREATE OR REPLACE FUNCTION retrieve_max_cnt(s_id integer) RETURNS integer
LANGUAGE SQL AS $$ SELECT max(n) FROM temp_smc(s_id); $$;
CREATE OR REPLACE FUNCTION mode_mark(param_sid integer) RETURNS float
LANGUAGE SQL
AS
$$
SELECT avg(mark)
FROM temp_smc(param_sid) t
LEFT JOIN (values (retrieve_max_cnt(param_sid), 1)) AS v (v1, v2) ON n =
v1
WHERE v1 IS NOT NULL
$$;
do
$$
DECLARE
stud record;
BEGIN
for stud in SELECT student_id FROM students
loop
raise notice '%) mode mark = %',
stud.student_id, mode_mark(stud.student_id);
end loop;
END
$$;
```

- temp_smc: для каждого студента считает количество каждой оценки.
- retrieve_max_cnt: возвращает максимум счетчиков для студента.
- mode_mark: среднее по оценкам, у которых частота равна максимуму (если несколько мод — усредняет их).
- DO-блок печатает mode mark для каждого студента.

*46*

```sql
CREATE OR REPLACE FUNCTION prof_per_SU(param_suid integer) RETURNS integer
LANGUAGE SQL AS $$
SELECT count(*) --ps.professor_id, su.structural_unit_id, su.full_title
FROM professors ps
JOIN employments es ON ps.professor_id = es.professor_id
JOIN structural_units su ON es.structural_unit_id =
su.structural_unit_id
WHERE su.structural_unit_id = param_suid
$$;
do
$$
DECLARE
su record;
BEGIN
for su in select structural_unit_id, full_title from structural_units
loop
raise notice '% Professors in %',
prof_per_SU(su.structural_unit_id), su.full_title;
end loop;
END
$$;
```

- Функция prof_per_SU считает число профессоров в заданном структурном подразделении.
- DO-блок перечисляет все подразделения и печатает их название с количеством.

*56*

```sql
CREATE OR REPLACE FUNCTION mark_change_log()
RETURNS TRIGGER
LANGUAGE PLPGSQL AS
$$
BEGIN
 IF NEW.mark <> OLD.mark THEN
 raise notice 'student % mark changed from % to %',
 NEW.student_id, OLD.mark, NEW.mark;
 END IF;
 RETURN NEW;
END;
$$;
CREATE OR REPLACE TRIGGER mark_change
AFTER UPDATE
ON field_comprehensions
FOR EACH ROW
EXECUTE FUNCTION mark_change_log();
UPDATE field_comprehensions SET mark = 3
FROM fields
WHERE fields.field_name = 'Иностранный язык'
 AND fields.field_id = field_comprehensions.field
 AND field_comprehensions.student_id = 847516;
select * from field_comprehensions fc
JOIN fields f on fc.field = f.field_id
where student_id = 847516 and mark = 3;
```

- Триггерная функция выводит NOTICE при изменении mark.
- Триггер AFTER UPDATE на field_comprehensions.
- Пример обновления оценки и выборка для проверки.

*66*

```sql
CREATE OR REPLACE FUNCTION mark_change_log()
RETURNS TRIGGER
LANGUAGE PLPGSQL AS
$$
BEGIN
 IF NEW.mark <> OLD.mark THEN
 raise notice 'student % mark changed from % to %',
 NEW.student_id, OLD.mark, NEW.mark;
 END IF;
 RETURN NEW;
END;
$$;
CREATE OR REPLACE TRIGGER mark_change
AFTER UPDATE
ON field_comprehensions
FOR EACH ROW
EXECUTE FUNCTION mark_change_log();
UPDATE field_comprehensions SET mark = 3
FROM fields
WHERE fields.field_name = 'Иностранный язык'
 AND fields.field_id = field_comprehensions.field
 AND field_comprehensions.student_id = 847516;
select * from field_comprehensions fc
JOIN fields f on fc.field = f.field_id
where student_id = 847516 and mark = 3;
-- 66
-- Если ЗП =0 => удалить преподавателя
CREATE OR REPLACE FUNCTION wage_fire_func()
RETURNS TRIGGER
LANGUAGE PLPGSQL AS
$$
BEGIN
IF NEW.salary = 0 THEN
DELETE FROM professors
 WHERE professor_id = NEW.professor_id;
END IF;
RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER wage_fire
AFTER UPDATE
ON professors
FOR EACH ROW
EXECUTE PROCEDURE wage_fire_func();
```

- Повторяет создание триггерной функции/триггера mark_change и пример обновления.
- Добавляет триггер wage_fire: после обновления professors, если зарплата стала 0 — удалить преподавателя.

---

# Task-3

```sql
CREATE OR REPLACE FUNCTION new_sick_notice()
RETURNS TRIGGER
LANGUAGE plpgsql AS
$$
BEGIN
  RAISE NOTICE '% has left sick', NEW.student_id;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS new_sick ON sick_leave_list;
CREATE TRIGGER new_sick
AFTER INSERT
ON sick_leave_list
FOR EACH ROW
EXECUTE FUNCTION new_sick_notice();
```

- Это триггер, который автоматически отправляет уведомление при добавлении новых записей в таблицу sick_leave_list
- В PL/pgSQL триггерной функции обычно нужно возвращать NEW (или NULL для BEFORE-триггеров). Также поля вставленной строки адресуются через NEW.<column>. Корректная версия может выглядеть так