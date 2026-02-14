@echo off
REM Скрипт для компиляции программы вручную (для Windows)
REM Используйте этот скрипт, если CLion не может собрать проект

echo ========================================
echo Компиляция database_lab8
echo ========================================

REM Укажите здесь путь к вашей установке PostgreSQL
set POSTGRESQL_PATH=C:\Program Files\PostgreSQL\17

REM Проверка наличия g++
where g++ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Компилятор g++ не найден!
    echo Установите MinGW или используйте CLion
    pause
    exit /b 1
)

echo Компиляция main.cpp...

g++ -o database_lab8.exe main.cpp ^
    -I"%POSTGRESQL_PATH%\include" ^
    -L"%POSTGRESQL_PATH%\lib" ^
    -lpq ^
    -std=c++17 ^
    -Wall

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Компиляция успешна!
    echo Исполняемый файл: database_lab8.exe
    echo ========================================
    echo.
    echo Запустить программу? (Y/N)
    set /p RUN_PROGRAM=
    if /i "%RUN_PROGRAM%"=="Y" (
        echo.
        database_lab8.exe
    )
) else (
    echo.
    echo ========================================
    echo ОШИБКА при компиляции!
    echo Проверьте:
    echo 1. Установлен ли PostgreSQL
    echo 2. Правильность пути в переменной POSTGRESQL_PATH
    echo 3. Наличие файла main.cpp
    echo ========================================
)

pause
