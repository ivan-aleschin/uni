# Скрипт для проверки и настройки SQL Server для лабораторной работы

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  SQL Server Setup для лабораторной   " -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Функция для проверки команды
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# 1. Проверка установки sqllocaldb
Write-Host "[1] Проверка SQL Server LocalDB..." -ForegroundColor Yellow

if (Test-Command "sqllocaldb") {
    Write-Host "✅ SQL Server LocalDB установлен!" -ForegroundColor Green
    
    # Получить версии
    Write-Host "`nДоступные версии LocalDB:" -ForegroundColor Cyan
    sqllocaldb versions
    
    # Проверить инстанс MSSQLLocalDB
    Write-Host "`nПроверка инстанса MSSQLLocalDB..." -ForegroundColor Yellow
    $instances = sqllocaldb info
    
    if ($instances -contains "MSSQLLocalDB") {
        Write-Host "✅ Инстанс MSSQLLocalDB существует" -ForegroundColor Green
        
        # Получить информацию об инстансе
        $info = sqllocaldb info MSSQLLocalDB
        Write-Host "`nИнформация об инстансе:" -ForegroundColor Cyan
        $info
        
        # Проверить, запущен ли инстанс
        $state = sqllocaldb info MSSQLLocalDB | Select-String "State:"
        if ($state -match "Running") {
            Write-Host "✅ Инстанс запущен!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Инстанс не запущен. Запускаем..." -ForegroundColor Yellow
            sqllocaldb start MSSQLLocalDB
            Start-Sleep -Seconds 3
            Write-Host "✅ Инстанс запущен!" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  Инстанс MSSQLLocalDB не найден. Создаём..." -ForegroundColor Yellow
        sqllocaldb create MSSQLLocalDB
        Start-Sleep -Seconds 2
        sqllocaldb start MSSQLLocalDB
        Start-Sleep -Seconds 3
        Write-Host "✅ Инстанс создан и запущен!" -ForegroundColor Green
    }
    
    $usingLocalDB = $true
} else {
    Write-Host "❌ SQL Server LocalDB не установлен" -ForegroundColor Red
    $usingLocalDB = $false
}

Write-Host ""

# 2. Проверка SQL Server Express
Write-Host "[2] Проверка SQL Server Express..." -ForegroundColor Yellow

$sqlServices = Get-Service | Where-Object {$_.Name -like "*SQL*" -and $_.Name -notlike "*Agent*" -and $_.Name -notlike "*Browser*"}

if ($sqlServices) {
    Write-Host "✅ Найдены службы SQL Server:" -ForegroundColor Green
    $sqlServices | Format-Table Name, DisplayName, Status -AutoSize
    
    $expressService = Get-Service -Name "MSSQL`$SQLEXPRESS" -ErrorAction SilentlyContinue
    if ($expressService) {
        if ($expressService.Status -eq "Running") {
            Write-Host "✅ SQL Server Express запущен!" -ForegroundColor Green
            $usingExpress = $true
        } else {
            Write-Host "⚠️  SQL Server Express не запущен. Пытаемся запустить..." -ForegroundColor Yellow
            try {
                Start-Service "MSSQL`$SQLEXPRESS"
                Write-Host "✅ SQL Server Express запущен!" -ForegroundColor Green
                $usingExpress = $true
            } catch {
                Write-Host "❌ Не удалось запустить SQL Server Express: $_" -ForegroundColor Red
                $usingExpress = $false
            }
        }
    } else {
        Write-Host "⚠️  SQL Server Express не найден" -ForegroundColor Yellow
        $usingExpress = $false
    }
} else {
    Write-Host "❌ SQL Server Express не установлен" -ForegroundColor Red
    $usingExpress = $false
}

Write-Host ""

# 3. Проверка подключения
Write-Host "[3] Проверка подключения к SQL Server..." -ForegroundColor Yellow

if (Test-Command "sqlcmd") {
    Write-Host "✅ sqlcmd доступен" -ForegroundColor Green
    
    if ($usingLocalDB) {
        Write-Host "`nТестирование подключения к LocalDB..." -ForegroundColor Cyan
        $result = sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT @@VERSION" -b
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Подключение к LocalDB успешно!" -ForegroundColor Green
        } else {
            Write-Host "❌ Не удалось подключиться к LocalDB" -ForegroundColor Red
        }
    }
    
    if ($usingExpress) {
        Write-Host "`nТестирование подключения к SQL Express..." -ForegroundColor Cyan
        $result = sqlcmd -S "localhost\SQLEXPRESS" -Q "SELECT @@VERSION" -b
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Подключение к SQL Express успешно!" -ForegroundColor Green
        } else {
            Write-Host "❌ Не удалось подключиться к SQL Express" -ForegroundColor Red
        }
    }
} else {
    Write-Host "⚠️  sqlcmd не найден (это нормально, необязательно)" -ForegroundColor Yellow
}

Write-Host ""

# 4. Итоги и рекомендации
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "           ИТОГИ ПРОВЕРКИ              " -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if ($usingLocalDB -or $usingExpress) {
    Write-Host "✅ SQL Server готов к работе!" -ForegroundColor Green
    Write-Host ""
    
    if ($usingLocalDB) {
        Write-Host "Используется: SQL Server LocalDB" -ForegroundColor Green
        Write-Host "Строка подключения в DbConfig.cs:" -ForegroundColor Cyan
        Write-Host '@"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=LabAB;Integrated Security=True;"' -ForegroundColor White
    }
    
    if ($usingExpress) {
        Write-Host "Используется: SQL Server Express" -ForegroundColor Green
        Write-Host "Строка подключения для DbConfig.cs:" -ForegroundColor Cyan
        Write-Host '@"Server=localhost\SQLEXPRESS;Database=LabAB;Trusted_Connection=True;"' -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Yellow
    Write-Host "1. Убедитесь, что строка подключения в DbConfig.cs корректна" -ForegroundColor White
    Write-Host "2. Запустите проект: dotnet run --project 1111/1111.csproj" -ForegroundColor White
    Write-Host "3. В меню выберите:" -ForegroundColor White
    Write-Host "   1 - Пересоздать таблицы" -ForegroundColor White
    Write-Host "   2 - Сгенерировать данные" -ForegroundColor White
    Write-Host "   3 - Создать отсортированные копии" -ForegroundColor White
    Write-Host "   5 - Merge-Join последовательный" -ForegroundColor White
    Write-Host "   6 - Merge-Join параллельный" -ForegroundColor White
    
} else {
    Write-Host "❌ SQL Server не готов к работе!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Необходимо установить SQL Server:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Вариант 1 (рекомендуется): SQL Server LocalDB" -ForegroundColor Cyan
    Write-Host "  - Через Visual Studio Installer:" -ForegroundColor White
    Write-Host "    1. Запустите Visual Studio Installer" -ForegroundColor White
    Write-Host "    2. Нажмите 'Изменить'" -ForegroundColor White
    Write-Host "    3. В 'Отдельные компоненты' найдите и отметьте:" -ForegroundColor White
    Write-Host "       'SQL Server Express LocalDB'" -ForegroundColor White
    Write-Host "    4. Нажмите 'Изменить' и дождитесь установки" -ForegroundColor White
    Write-Host ""
    Write-Host "Вариант 2: SQL Server Express" -ForegroundColor Cyan
    Write-Host "  - Скачайте с: https://www.microsoft.com/en-us/sql-server/sql-server-downloads" -ForegroundColor White
    Write-Host "  - Выберите 'Express' версию" -ForegroundColor White
    Write-Host "  - Следуйте инструкциям установщика" -ForegroundColor White
    Write-Host ""
    Write-Host "После установки запустите этот скрипт снова!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Для подробной информации см. INSTALL_SQL_SERVER.md" -ForegroundColor Cyan
Write-Host ""

# Ждём нажатия клавиши
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

