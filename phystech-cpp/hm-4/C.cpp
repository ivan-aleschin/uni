#include <vector>
#include <iostream>
#include <windows.h>
#include <string>

using namespace std;

struct Time {
    unsigned int year: 7;
    unsigned int month: 4;
    unsigned int day: 5;
    unsigned int hours: 5;
    unsigned int mins: 6;
    unsigned int secs: 6;
    unsigned int milisecs: 10;

    ~Time() {
        cout << "Время удалено!" << endl;
    }
};

int main()
{
    SetConsoleOutputCP(CP_UTF8);

    int tmp{0};
    Time ad;

    cout << "Введите год двузначным числом (начиная с 2000 года) (0-99): " << endl;
    cin >> tmp;
    ad.year = tmp;
    cout << "Введите месяц (1-12): " << endl;
    cin >> tmp;
    ad.month = tmp;
    cout << "Введите день (1-31): " << endl;
    cin >> tmp;
    ad.day = tmp;

    cout << "Введите часы (0-24): " << endl;
    cin >> tmp;
    ad.hours = tmp;
    cout << "Введите минуты (0-60): " << endl;
    cin >> tmp;
    ad.mins = tmp;
    cout << "Введите секунды (0-60): " << endl;
    cin >> tmp;
    ad.secs = tmp;
    cout << "Введите милисекунды (0-999): " << endl;
    cin >> tmp;
    ad.milisecs = tmp;

    cout << "\nВведенная дата: " << ad.day << "." << ad.month << "." << ad.year << " ";
    cout << ad.hours << ":" << ad.mins << ":" << ad.secs << ":" << ad.milisecs << endl;
    cout << "Размер структуры данных о времени: " << sizeof(ad) << " байт" << endl;

    return 0;
}
