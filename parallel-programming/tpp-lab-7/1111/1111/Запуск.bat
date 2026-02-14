@echo off
chcp 1251 >nul
cls
echo ========================================
echo   ЛАБОРАТОРНАЯ РАБОТА - ПАРАЛЛЕЛЬНЫЙ JOIN
echo ========================================
echo.
echo Запуск приложения...
echo.

cd /d "%~dp0bin\Release\net9.0"

if not exist "1111.exe" (
    echo ОШИБКА: Файл 1111.exe не найден!
    echo.
    echo Сначала соберите проект:
    echo    dotnet build --configuration Release
    echo.
    pause
    exit /b 1
)

1111.exe

if errorlevel 1 (
    echo.
    echo Программа завершилась с ошибкой!
    echo.
)

pause

