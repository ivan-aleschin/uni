# 🗄️ Установка SQL Server для лабораторной работы

## ⚠️ Важно: LocalDB не установлен на вашей системе!

Чтобы запустить эту лабораторную работу, вам нужно установить SQL Server LocalDB или SQL Server Express.

---

## 📥 Вариант 1: SQL Server LocalDB (Рекомендуется)

LocalDB - это облегченная версия SQL Server для разработчиков.

### Установка через Visual Studio:

1. **Откройте Visual Studio Installer**
   - Найдите в меню "Пуск": "Visual Studio Installer"

2. **Выберите "Изменить" для вашей установки Visual Studio**

3. **Во вкладке "Отдельные компоненты" найдите и отметьте:**
   - ✅ **SQL Server Express 2019 LocalDB** (или новее)

4. **Нажмите "Изменить"** и дождитесь установки

### Установка отдельно (без Visual Studio):

1. **Скачайте SQL Server Express:**
   - https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   - Нажмите "Download now" под "Express"

2. **Запустите установщик:**
   - Выберите **"Basic"** (Базовая установка)
   - Следуйте инструкциям установщика

3. **После установки проверьте:**
   ```powershell
   sqllocaldb versions
   ```
   Должно показать версию, например: `MSSQLLocalDB`

4. **Создайте и запустите инстанс:**
   ```powershell
   sqllocaldb create MSSQLLocalDB
   sqllocaldb start MSSQLLocalDB
   ```

### Проверка установки:
```powershell
# Проверить доступные версии
sqllocaldb versions

# Получить информацию об инстансе
sqllocaldb info MSSQLLocalDB

# Запустить инстанс (если не запущен)
sqllocaldb start MSSQLLocalDB
```

### Строка подключения (уже в коде):
```csharp
@"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=LabAB;Integrated Security=True;"
```

---

## 📥 Вариант 2: SQL Server Express (Полная версия)

Если LocalDB не подходит или вы хотите полнофункциональный SQL Server:

### Установка:

1. **Скачайте SQL Server 2022 Express:**
   - https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   - Нажмите "Download now" под "Express"

2. **Запустите установщик:**
   - Выберите **"Custom"** (Пользовательская)
   - Укажите путь для загрузки установочных файлов
   - Дождитесь скачивания

3. **В окне установки:**
   - Выберите **"New SQL Server stand-alone installation"**
   - Примите лицензионное соглашение
   - Выберите компоненты: **Database Engine Services** ✅
   - Instance Configuration: **Default instance** (SQLEXPRESS)
   - Authentication Mode: **Windows Authentication** (рекомендуется)
   - Добавьте текущего пользователя как SQL Server Administrator
   - Завершите установку

4. **После установки измените DbConfig.cs:**
   ```csharp
   public const string ConnectionString =
       @"Server=localhost\SQLEXPRESS;Database=LabAB;Trusted_Connection=True;";
   ```

### Проверка установки:
```powershell
# Проверить службу SQL Server
Get-Service | Where-Object {$_.Name -like "*SQL*"}

# Должна быть запущена служба MSSQL$SQLEXPRESS (Running)
```

---

## 📥 Вариант 3: Использование SQLite (Альтернатива)

Если SQL Server не устанавливается, можно адаптировать код под SQLite (уже есть в зависимостях).

### Для этого нужно изменить код:

1. **Изменить DbConfig.cs:**
```csharp
using System.Data.SQLite;

namespace LabAB
{
    internal static class DbConfig
    {
        public const string ConnectionString = 
            @"Data Source=LabAB.db;Version=3;";

        public static SQLiteConnection CreateConnection()
        {
            return new SQLiteConnection(ConnectionString);
        }
    }
}
```

2. **Изменить все файлы:**
   - Заменить `SqlConnection` на `SQLiteConnection`
   - Заменить `SqlCommand` на `SQLiteCommand`
   - Заменить `SqlDataReader` на `SQLiteDataReader`
   - Заменить `SqlBulkCopy` на обычные INSERT (SQLite не поддерживает BulkCopy)
   - Изменить синтаксис SQL (SQLite отличается от T-SQL)

**Примечание:** Это потребует значительных изменений кода. Рекомендуется установить SQL Server.

---

## 🚀 После установки SQL Server

### 1. Запустить службу/инстанс:

**Для LocalDB:**
```powershell
sqllocaldb start MSSQLLocalDB
```

**Для SQL Server Express:**
```powershell
# Запустить службу
net start MSSQL$SQLEXPRESS
```

### 2. Собрать проект:
```powershell
cd C:\Dev\Workspace\tpp-lab-7\1111
dotnet build
```

### 3. Запустить лабораторную:
```powershell
dotnet run --project 1111/1111.csproj
```

### 4. В меню выбрать последовательно:
```
1 - Пересоздать таблицы (создаст базу данных LabAB и таблицы)
2 - Сгенерировать данные
3 - Создать отсортированные копии
5 - Запустить Merge-Join последовательный
6 - Запустить Merge-Join параллельный
```

---

## 🔧 Устранение проблем

### Ошибка: "Cannot open database"

**Решение 1 - Создать базу вручную:**
```sql
CREATE DATABASE LabAB;
```

**Решение 2 - Разрешить создание БД в строке подключения:**

Измените DbConfig.cs:
```csharp
public const string ConnectionString =
    @"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=LabAB;Integrated Security=True;AttachDbFilename=|DataDirectory|\LabAB.mdf;";
```

### Ошибка: "Login failed for user"

**Решение:**
- Используйте Windows Authentication (Integrated Security=True)
- Или создайте SQL пользователя:
```sql
CREATE LOGIN labuser WITH PASSWORD = 'Lab123!';
USE LabAB;
CREATE USER labuser FOR LOGIN labuser;
ALTER ROLE db_owner ADD MEMBER labuser;
```

Измените строку подключения:
```csharp
@"Server=(localdb)\MSSQLLocalDB;Database=LabAB;User Id=labuser;Password=Lab123!;"
```

### Ошибка: "A network-related error occurred"

**Решение:**
```powershell
# Остановить и пересоздать LocalDB инстанс
sqllocaldb stop MSSQLLocalDB
sqllocaldb delete MSSQLLocalDB
sqllocaldb create MSSQLLocalDB
sqllocaldb start MSSQLLocalDB
```

### Порт занят / SQL Server не запускается

**Решение:**
```powershell
# Проверить запущенные службы SQL Server
Get-Service | Where-Object {$_.Name -like "*SQL*"}

# Остановить конфликтующие службы
net stop "SQL Server (MSSQLSERVER)"
net start MSSQL$SQLEXPRESS
```

---

## 📊 Проверка работы SQL Server

### Через PowerShell:

```powershell
# Тест подключения к LocalDB
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT @@VERSION"

# Тест подключения к SQL Express
sqlcmd -S "localhost\SQLEXPRESS" -Q "SELECT @@VERSION"

# Список баз данных
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT name FROM sys.databases"
```

### Через SQL Server Management Studio (SSMS):

1. **Скачать SSMS:** https://aka.ms/ssmsfullsetup
2. **Подключиться:**
   - Server name: `(localdb)\MSSQLLocalDB` или `localhost\SQLEXPRESS`
   - Authentication: **Windows Authentication**
3. **Проверить базу LabAB после запуска программы**

---

## ✅ Готово!

После установки SQL Server вернитесь к основной инструкции в **README.md** для запуска лабораторной работы.

**Если возникли проблемы, проверьте:**
- ✅ SQL Server установлен и запущен
- ✅ База данных LabAB создана (или автоматически создастся)
- ✅ Пользователь имеет права на создание таблиц
- ✅ Файрволл не блокирует SQL Server

**Удачи! 🚀**

