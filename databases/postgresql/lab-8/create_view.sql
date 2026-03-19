-- Скрипт для создания представления (Задание 2.3)
-- Выполните этот скрипт в DataGrip для демонстрации работы с представлениями

-- Удаление представления если оно существует
DROP VIEW IF EXISTS student_marks_view;

-- Создание представления для просмотра оценок студентов
CREATE VIEW student_marks_view AS
SELECT
    S.STUDENT_ID,
    S.SURNAME,
    S.NAME,
    S.GROUP_NUMBER,
    F.FIELD_NAME,
    F_C.MARK
FROM STUDENT S
JOIN FIELD_COMPREHENSION F_C ON S.STUDENT_ID = F_C.STUDENT_ID
JOIN FIELD F ON F.FIELD_ID = F_C.FIELD;

-- Предоставление прав на представление
GRANT SELECT ON student_marks_view TO sab_junior;
GRANT ALL ON student_marks_view TO sab_admin;

-- Пример использования представления
SELECT * FROM student_marks_view WHERE STUDENT_ID = 856271;

-- Проверка созданного представления
SELECT viewname, definition
FROM pg_views
WHERE viewname = 'student_marks_view';

