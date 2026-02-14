-- Скрипт для создания ролей пользователей для лабораторной работы 8
-- Выполните этот скрипт в DataGrip перед запуском программы

-- Создание роли администратора
DROP ROLE IF EXISTS sab_admin;
CREATE ROLE sab_admin WITH
    LOGIN
    PASSWORD '123456'
    SUPERUSER
    CREATEDB
    CREATEROLE;

COMMENT ON ROLE sab_admin IS 'Роль администратора с полными правами';

-- Создание роли junior пользователя (только чтение)
DROP ROLE IF EXISTS sab_junior;
CREATE ROLE sab_junior WITH
    LOGIN
    PASSWORD '123456'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

COMMENT ON ROLE sab_junior IS 'Роль пользователя с правами только на чтение';

-- Предоставление прав junior пользователю (только SELECT)
GRANT CONNECT ON DATABASE students TO sab_junior;
GRANT USAGE ON SCHEMA public TO sab_junior;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sab_junior;

-- Предоставление полных прав администратору
GRANT ALL PRIVILEGES ON DATABASE students TO sab_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sab_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sab_admin;

-- Для будущих таблиц
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO sab_junior;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO sab_admin;

-- Проверка созданных ролей
SELECT rolname, rolsuper, rolcreatedb, rolcanlogin
FROM pg_roles
WHERE rolname IN ('sab_admin', 'sab_junior');

