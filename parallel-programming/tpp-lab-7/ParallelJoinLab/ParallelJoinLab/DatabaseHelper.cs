using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Linq;

namespace ParallelJoinLab
{
    public class DatabaseHelper
    {
        private readonly string _connectionString;
        private readonly string _databasePath;

        public DatabaseHelper()
        {
            _databasePath = "lab_database.db";
            _connectionString = $"Data Source={_databasePath};Version=3;";
            InitializeDatabase();
        }

        private void InitializeDatabase()
        {
            if (!File.Exists(_databasePath))
            {
                SQLiteConnection.CreateFile(_databasePath);
            }

            using var connection = new SQLiteConnection(_connectionString);
            connection.Open();

            // Создание таблиц БЕЗ объявления ключа (без PRIMARY KEY)
            var createStudentsTable = @"
                CREATE TABLE IF NOT EXISTS Students (
                    StudentKey NCHAR(4) NOT NULL,
                    FirstName NVARCHAR(50),
                    LastName NVARCHAR(50),
                    Age INTEGER,
                    AverageGrade REAL,
                    IsActive INTEGER
                )";

            var createCoursesTable = @"
                CREATE TABLE IF NOT EXISTS Courses (
                    CourseKey NCHAR(4) NOT NULL,
                    CourseName NVARCHAR(50),
                    Credits INTEGER,
                    Price REAL,
                    Duration INTEGER,
                    IsOnline INTEGER
                )";

            ExecuteNonQuery(createStudentsTable, connection);
            ExecuteNonQuery(createCoursesTable, connection);
        }

        public void GenerateTestData(int recordCount = 10000)
        {
            using var connection = new SQLiteConnection(_connectionString);
            connection.Open();

            ExecuteNonQuery("DELETE FROM Students", connection);
            ExecuteNonQuery("DELETE FROM Courses", connection);

            var random = new Random();
            var firstNames = new[] { "Иван", "Петр", "Мария", "Анна", "Сергей", "Ольга" };
            var lastNames = new[] { "Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов" };
            var courseNames = new[] { "Математика", "Физика", "Химия", "Информатика", "История" };

            // Генерация студентов
            for (int i = 0; i < recordCount; i++)
            {
                var key = GenerateKey(random, 4);
                var firstName = firstNames[random.Next(firstNames.Length)];
                var lastName = lastNames[random.Next(lastNames.Length)];
                var age = random.Next(18, 25);
                var avgGrade = Math.Round(random.NextDouble() * 3 + 2, 2);
                var isActive = random.Next(2);

                using var cmd = new SQLiteCommand(
                    "INSERT INTO Students (StudentKey, FirstName, LastName, Age, AverageGrade, IsActive) " +
                    "VALUES (@key, @firstName, @lastName, @age, @avgGrade, @isActive)",
                    connection);
                
                cmd.Parameters.AddWithValue("@key", key);
                cmd.Parameters.AddWithValue("@firstName", firstName);
                cmd.Parameters.AddWithValue("@lastName", lastName);
                cmd.Parameters.AddWithValue("@age", age);
                cmd.Parameters.AddWithValue("@avgGrade", avgGrade);
                cmd.Parameters.AddWithValue("@isActive", isActive);
                cmd.ExecuteNonQuery();
            }

            // Генерация курсов
            for (int i = 0; i < recordCount; i++)
            {
                var key = GenerateKey(random, 4);
                var courseName = courseNames[random.Next(courseNames.Length)];
                var credits = random.Next(1, 6);
                var price = Math.Round(random.NextDouble() * 50000 + 10000, 2);
                var duration = random.Next(30, 180);
                var isOnline = random.Next(2);

                using var cmd = new SQLiteCommand(
                    "INSERT INTO Courses (CourseKey, CourseName, Credits, Price, Duration, IsOnline) " +
                    "VALUES (@key, @courseName, @credits, @price, @duration, @isOnline)",
                    connection);
                
                cmd.Parameters.AddWithValue("@key", key);
                cmd.Parameters.AddWithValue("@courseName", courseName);
                cmd.Parameters.AddWithValue("@credits", credits);
                cmd.Parameters.AddWithValue("@price", price);
                cmd.Parameters.AddWithValue("@duration", duration);
                cmd.Parameters.AddWithValue("@isOnline", isOnline);
                cmd.ExecuteNonQuery();
            }
        }

        private string GenerateKey(Random random, int length)
        {
            var letters = "ABCDEFGH";
            var keyChars = new char[length];
            
            for (int i = 0; i < length; i++)
            {
                keyChars[i] = letters[random.Next(letters.Length)];
            }
            
            return new string(keyChars);
        }

        public void CreateSortedTables()
        {
            using var connection = new SQLiteConnection(_connectionString);
            connection.Open();

            ExecuteNonQuery("DROP TABLE IF EXISTS Students_srt", connection);
            ExecuteNonQuery("DROP TABLE IF EXISTS Courses_srt", connection);

            ExecuteNonQuery("CREATE TABLE Students_srt AS SELECT * FROM Students ORDER BY StudentKey", connection);
            ExecuteNonQuery("CREATE TABLE Courses_srt AS SELECT * FROM Courses ORDER BY CourseKey", connection);
        }

        public List<Student> GetStudents(bool sorted = false)
        {
            var tableName = sorted ? "Students_srt" : "Students";
            return GetData<Student>($"SELECT * FROM {tableName}", 
                reader => new Student(
                    reader["StudentKey"].ToString(),
                    reader["FirstName"].ToString(),
                    reader["LastName"].ToString(),
                    Convert.ToInt32(reader["Age"]),
                    Convert.ToDouble(reader["AverageGrade"]),
                    Convert.ToInt32(reader["IsActive"]) == 1
                ));
        }

        public List<Course> GetCourses(bool sorted = false)
        {
            var tableName = sorted ? "Courses_srt" : "Courses";
            return GetData<Course>($"SELECT * FROM {tableName}",
                reader => new Course(
                    reader["CourseKey"].ToString(),
                    reader["CourseName"].ToString(),
                    Convert.ToInt32(reader["Credits"]),
                    Convert.ToDouble(reader["Price"]),
                    Convert.ToInt32(reader["Duration"]),
                    Convert.ToInt32(reader["IsOnline"]) == 1
                ));
        }

        public string AnalyzeDuplicates()
        {
            var students = GetStudents();
            var courses = GetCourses();

            var studentDuplicates = students
                .GroupBy(s => s.Key)
                .Where(g => g.Count() > 1)
                .OrderByDescending(g => g.Count())
                .Take(10)
                .ToList();

            var courseDuplicates = courses
                .GroupBy(c => c.Key)
                .Where(g => g.Count() > 1)
                .OrderByDescending(g => g.Count())
                .Take(10)
                .ToList();

            string result = "Анализ дубликатов ключей:\nСтуденты:\n";
            foreach (var group in studentDuplicates)
            {
                result += $"Ключ '{group.Key}': {group.Count()} записей\n";
            }

            result += "\nКурсы:\n";
            foreach (var group in courseDuplicates)
            {
                result += $"Ключ '{group.Key}': {group.Count()} записей\n";
            }

            if (!studentDuplicates.Any() && !courseDuplicates.Any())
            {
                result = "Дубликаты ключей не найдены. Увеличьте количество записей для появления дубликатов.";
            }

            return result;
        }

        private void ExecuteNonQuery(string query, SQLiteConnection connection)
        {
            using var cmd = new SQLiteCommand(query, connection);
            cmd.ExecuteNonQuery();
        }

        private List<T> GetData<T>(string query, Func<SQLiteDataReader, T> mapper)
        {
            var result = new List<T>();
            
            using var connection = new SQLiteConnection(_connectionString);
            connection.Open();
            
            using var cmd = new SQLiteCommand(query, connection);
            using var reader = cmd.ExecuteReader();
            
            while (reader.Read())
            {
                result.Add(mapper(reader));
            }
            
            return result;
        }
    }
}