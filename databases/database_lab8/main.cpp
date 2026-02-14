#include <iostream>
#include <cstring>
#include <cstdlib>
#include <libpq-fe.h>
#include <string>
#include <sstream>

using namespace std;

// Глобальная переменная для хранения роли пользователя
string currentUserRole = "";

/*
    Функция выхода из программы с сообщением об ошибке.
*/
void err_exit(PGconn *conn) {
    PQfinish(conn);
    exit(1);
}

/*
   Функция печати результата запроса на экран
        *conn -> дескриптор подключения к серверу
        query -> текст запроса
*/
void print_query(PGconn *conn, const char* query) {
    PGresult *res = PQexec(conn, query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK && PQresultStatus(res) != PGRES_COMMAND_OK) {
        cout << "Ошибка выполнения запроса: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    int rows = PQntuples(res);
    int cols = PQnfields(res);

    if (rows == 0) {
        cout << "Нет данных для отображения." << endl;
        PQclear(res);
        return;
    }

    // Вывод заголовков
    for(int j = 0; j < cols; j++) {
        cout << PQfname(res, j) << "\t";
    }
    cout << endl;
    cout << string(cols * 16, '-') << endl;

    // Вывод данных
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++) {
            cout << PQgetvalue(res, i, j) << "\t";
        }
        cout << endl;
    }

    PQclear(res);
}

/*
    Функция обнаружения SQL инъекций
*/
bool detectSQLInjection(const string& input) {
    string dangerous[] = {
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER",
        "CREATE", "TRUNCATE", "--", "/*", "*/", ";",
        "UNION", "SELECT", "EXEC", "EXECUTE"
    };

    string upperInput = input;
    for(auto &c : upperInput) c = toupper(c);

    for(const auto& keyword : dangerous) {
        if(upperInput.find(keyword) != string::npos) {
            return true;
        }
    }

    // Проверка на множественные кавычки
    int quoteCount = 0;
    for(char c : input) {
        if(c == '\'' || c == '"') quoteCount++;
    }
    if(quoteCount > 2) return true;

    return false;
}

/*
    Функция экранирования кавычек для защиты от SQL инъекций
*/
string escapeSQLString(PGconn *conn, const string& input) {
    char *escaped = new char[input.length() * 2 + 1];
    PQescapeStringConn(conn, escaped, input.c_str(), input.length(), NULL);
    string result(escaped);
    delete[] escaped;
    return result;
}

/*
    Задание 2.1 - Функция поиска оценки студента с защитой от SQL инъекций
    Использует параметризированный запрос
*/
void findStudentMark(PGconn *conn, const string& studentId, const string& fieldName) {
    // Проверка на SQL инъекцию
    if(detectSQLInjection(studentId) || detectSQLInjection(fieldName)) {
        cout << "\n⚠️  ВНИМАНИЕ! Обнаружена попытка SQL-инъекции!" << endl;
        cout << "Пользователю вынесено предупреждение." << endl;
        cout << "Попытка выполнения опасного запроса заблокирована." << endl;
        return;
    }

    const char *paramValues[2];
    paramValues[0] = studentId.c_str();
    paramValues[1] = fieldName.c_str();

    const char *query =
        "SELECT S.STUDENT_ID, S.SURNAME, S.NAME, F.FIELD_NAME, F_C.MARK "
        "FROM STUDENT S "
        "JOIN FIELD_COMPREHENSION F_C ON S.STUDENT_ID = F_C.STUDENT_ID "
        "JOIN FIELD F ON F.FIELD_ID = F_C.FIELD "
        "WHERE S.STUDENT_ID = $1::INTEGER AND F.FIELD_NAME = $2";

    PGresult *res = PQexecParams(conn, query, 2, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Ошибка выполнения запроса: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    int rows = PQntuples(res);
    int cols = PQnfields(res);

    if(rows == 0) {
        cout << "Студент с таким ID или дисциплина не найдены." << endl;
    } else {
        cout << "\nРезультат поиска:" << endl;
        for(int j = 0; j < cols; j++) {
            cout << PQfname(res, j) << "\t";
        }
        cout << endl;
        cout << string(cols * 16, '-') << endl;

        for(int i = 0; i < rows; i++) {
            for(int j = 0; j < cols; j++) {
                cout << PQgetvalue(res, i, j) << "\t";
            }
            cout << endl;
        }
    }

    PQclear(res);
}

/*
    Задание 3.2 - CRUD операции для администратора
*/
void addMark(PGconn *conn, const string& studentId, const string& fieldId, const string& mark) {
    if(currentUserRole != "admin") {
        cout << "Доступ запрещен. Требуются права администратора." << endl;
        return;
    }

    const char *paramValues[3];
    paramValues[0] = studentId.c_str();
    paramValues[1] = fieldId.c_str();
    paramValues[2] = mark.c_str();

    const char *query = "INSERT INTO FIELD_COMPREHENSION (STUDENT_ID, FIELD, MARK) VALUES ($1::INTEGER, $2::INTEGER, $3::INTEGER)";

    PGresult *res = PQexecParams(conn, query, 3, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) == PGRES_COMMAND_OK) {
        cout << "Оценка успешно добавлена." << endl;
    } else {
        cout << "Ошибка при добавлении оценки: " << PQerrorMessage(conn) << endl;
    }

    PQclear(res);
}

void updateMark(PGconn *conn, const string& studentId, const string& fieldId, const string& newMark) {
    if(currentUserRole != "admin") {
        cout << "Доступ запрещен. Требуются права администратора." << endl;
        return;
    }

    const char *paramValues[3];
    paramValues[0] = newMark.c_str();
    paramValues[1] = studentId.c_str();
    paramValues[2] = fieldId.c_str();

    const char *query = "UPDATE FIELD_COMPREHENSION SET MARK = $1::INTEGER WHERE STUDENT_ID = $2::INTEGER AND FIELD = $3::INTEGER";

    PGresult *res = PQexecParams(conn, query, 3, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) == PGRES_COMMAND_OK) {
        cout << "Оценка успешно обновлена." << endl;
    } else {
        cout << "Ошибка при обновлении оценки: " << PQerrorMessage(conn) << endl;
    }

    PQclear(res);
}

void deleteMark(PGconn *conn, const string& studentId, const string& fieldId) {
    if(currentUserRole != "admin") {
        cout << "Доступ запрещен. Требуются права администратора." << endl;
        return;
    }

    const char *paramValues[2];
    paramValues[0] = studentId.c_str();
    paramValues[1] = fieldId.c_str();

    const char *query = "DELETE FROM FIELD_COMPREHENSION WHERE STUDENT_ID = $1::INTEGER AND FIELD = $2::INTEGER";

    PGresult *res = PQexecParams(conn, query, 2, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) == PGRES_COMMAND_OK) {
        cout << "Оценка успешно удалена." << endl;
    } else {
        cout << "Ошибка при удалении оценки: " << PQerrorMessage(conn) << endl;
    }

    PQclear(res);
}

/*
    Задание 3.1 - Функции для работы с разными ролями пользователей
*/
void showAllMarksForUser(PGconn *conn, const string& studentId) {
    const char *paramValues[1];
    paramValues[0] = studentId.c_str();

    const char *query =
        "SELECT S.SURNAME, S.NAME, S.GROUP_NUMBER, F.FIELD_NAME, F_C.MARK "
        "FROM STUDENT S "
        "JOIN FIELD_COMPREHENSION F_C ON S.STUDENT_ID = F_C.STUDENT_ID "
        "JOIN FIELD F ON F.FIELD_ID = F_C.FIELD "
        "WHERE S.STUDENT_ID = $1::INTEGER";

    PGresult *res = PQexecParams(conn, query, 1, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Ошибка выполнения запроса: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    int rows = PQntuples(res);
    int cols = PQnfields(res);

    cout << "\nВсе оценки студента:" << endl;
    for(int j = 0; j < cols; j++) {
        cout << PQfname(res, j) << "\t";
    }
    cout << endl;
    cout << string(cols * 16, '-') << endl;

    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++) {
            cout << PQgetvalue(res, i, j) << "\t";
        }
        cout << endl;
    }

    PQclear(res);
}

void searchStudent(PGconn *conn, const string& surname, const string& name, const string& groupNumber) {
    if(detectSQLInjection(surname) || detectSQLInjection(name) || detectSQLInjection(groupNumber)) {
        cout << "\n⚠️  ВНИМАНИЕ! Обнаружена попытка SQL-инъекции!" << endl;
        cout << "Пользователю вынесено предупреждение." << endl;
        return;
    }

    const char *paramValues[3];
    paramValues[0] = surname.c_str();
    paramValues[1] = name.c_str();
    paramValues[2] = groupNumber.c_str();

    const char *query =
        "SELECT S.STUDENT_ID, S.SURNAME, S.NAME, S.GROUP_NUMBER, F.FIELD_NAME, F_C.MARK "
        "FROM STUDENT S "
        "JOIN FIELD_COMPREHENSION F_C ON S.STUDENT_ID = F_C.STUDENT_ID "
        "JOIN FIELD F ON F.FIELD_ID = F_C.FIELD "
        "WHERE S.SURNAME = $1 AND S.NAME = $2 AND S.GROUP_NUMBER = $3::INTEGER";

    PGresult *res = PQexecParams(conn, query, 3, NULL, paramValues, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Ошибка выполнения запроса: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    int rows = PQntuples(res);
    int cols = PQnfields(res);

    if(rows == 0) {
        cout << "Студент не найден." << endl;
    } else {
        cout << "\nРезультат поиска:" << endl;
        for(int j = 0; j < cols; j++) {
            cout << PQfname(res, j) << "\t";
        }
        cout << endl;
        cout << string(cols * 16, '-') << endl;

        for(int i = 0; i < rows; i++) {
            for(int j = 0; j < cols; j++) {
                cout << PQgetvalue(res, i, j) << "\t";
            }
            cout << endl;
        }
    }

    PQclear(res);
}

void adminMenu(PGconn *conn) {
    int choice;
    do {
        cout << "\n=== МЕНЮ АДМИНИСТРАТОРА ===" << endl;
        cout << "1. Добавить оценку студенту" << endl;
        cout << "2. Изменить оценку студента" << endl;
        cout << "3. Удалить оценку студента" << endl;
        cout << "4. Просмотреть все оценки студента" << endl;
        cout << "5. Поиск оценки по ID студента и дисциплине" << endl;
        cout << "0. Выход" << endl;
        cout << "Выберите действие: ";
        cin >> choice;
        cin.ignore();

        string studentId, fieldId, mark, fieldName;

        switch(choice) {
            case 1:
                cout << "Введите ID студента: ";
                getline(cin, studentId);
                cout << "Введите ID дисциплины: ";
                getline(cin, fieldId);
                cout << "Введите оценку: ";
                getline(cin, mark);
                addMark(conn, studentId, fieldId, mark);
                break;
            case 2:
                cout << "Введите ID студента: ";
                getline(cin, studentId);
                cout << "Введите ID дисциплины: ";
                getline(cin, fieldId);
                cout << "Введите новую оценку: ";
                getline(cin, mark);
                updateMark(conn, studentId, fieldId, mark);
                break;
            case 3:
                cout << "Введите ID студента: ";
                getline(cin, studentId);
                cout << "Введите ID дисциплины: ";
                getline(cin, fieldId);
                deleteMark(conn, studentId, fieldId);
                break;
            case 4:
                cout << "Введите ID студента: ";
                getline(cin, studentId);
                showAllMarksForUser(conn, studentId);
                break;
            case 5:
                cout << "Введите ID студента: ";
                getline(cin, studentId);
                cout << "Введите название дисциплины: ";
                getline(cin, fieldName);
                findStudentMark(conn, studentId, fieldName);
                break;
            case 0:
                cout << "Выход из системы..." << endl;
                break;
            default:
                cout << "Неверный выбор!" << endl;
        }
    } while(choice != 0);
}

void userMenu(PGconn *conn) {
    int choice;
    do {
        cout << "\n=== МЕНЮ ПОЛЬЗОВАТЕЛЯ ===" << endl;
        cout << "1. Просмотреть все мои оценки" << endl;
        cout << "2. Поиск студента по ФИО и группе" << endl;
        cout << "3. Попытка изменить оценку (тест SQL-инъекции)" << endl;
        cout << "0. Выход" << endl;
        cout << "Выберите действие: ";
        cin >> choice;
        cin.ignore();

        string studentId, surname, name, groupNumber;

        switch(choice) {
            case 1:
                cout << "Введите ваш ID студента: ";
                getline(cin, studentId);
                showAllMarksForUser(conn, studentId);
                break;
            case 2:
                cout << "Введите фамилию: ";
                getline(cin, surname);
                cout << "Введите имя: ";
                getline(cin, name);
                cout << "Введите номер группы: ";
                getline(cin, groupNumber);
                searchStudent(conn, surname, name, groupNumber);
                break;
            case 3:
                cout << "\nПопытка выполнить SQL-инъекцию для изменения оценки..." << endl;
                cout << "Введите 'вредоносный' запрос: ";
                getline(cin, studentId);
                // Пытаемся выполнить запрос с потенциальной инъекцией
                findStudentMark(conn, studentId, "'; UPDATE FIELD_COMPREHENSION SET MARK=5; --");
                break;
            case 0:
                cout << "Выход из системы..." << endl;
                break;
            default:
                cout << "Неверный выбор!" << endl;
        }
    } while(choice != 0);
}

int main() {
    setlocale(LC_ALL, "Russian");

    cout << "=== СИСТЕМА УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ СТУДЕНТОВ ===" << endl;
    cout << "\nВыберите тип пользователя:" << endl;
    cout << "1. Администратор (admin)" << endl;
    cout << "2. Пользователь (junior)" << endl;
    cout << "Ваш выбор: ";

    int userType;
    cin >> userType;
    cin.ignore();

    string dbUser, dbPassword;

    if(userType == 1) {
        currentUserRole = "admin";
        cout << "\nВведите имя пользователя БД (например, sab_admin): ";
        getline(cin, dbUser);
        cout << "Введите пароль: ";
        getline(cin, dbPassword);
    } else {
        currentUserRole = "junior";
        cout << "\nВведите имя пользователя БД (например, sab_junior): ";
        getline(cin, dbUser);
        cout << "Введите пароль: ";
        getline(cin, dbPassword);
    }

    // Формирование строки подключения
    string connString = "host=localhost port=5432 dbname=students user=" + dbUser + " password=" + dbPassword;

    PGconn *conn = PQconnectdb(connString.c_str());

    if (PQstatus(conn) == CONNECTION_BAD) {
        cerr << "Ошибка подключения к базе данных: " << PQerrorMessage(conn) << endl;
        err_exit(conn);
    }

    cout << "\n✓ Успешное подключение к базе данных!" << endl;
    cout << "Роль пользователя: " << currentUserRole << endl;

    if(currentUserRole == "admin") {
        adminMenu(conn);
    } else {
        userMenu(conn);
    }

    PQfinish(conn);
    cout << "\nСоединение с базой данных закрыто." << endl;

    return 0;
}