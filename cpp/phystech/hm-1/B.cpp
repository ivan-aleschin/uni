#include <iostream>
#include <windows.h>
#include <iomanip>
#include <cmath>

int main() {
    using namespace std;
    SetConsoleOutputCP(CP_UTF8);

    int charin;
    double intin;
    const double  trans{3.3 * pow(10, -10)}; //ввод константы для Кулонов, первый случай
    cout << "___Перевод из Си в СГСЭ___\n";
    cout << "Введите число: ";
    cin >> intin;
    cout << "Доступные единицы измерений (цифра от 1 до 8): \n 1) Кл;\n 2) Н;\n 2) Дж;\n 3) Па;\n 4) В;\n 5) Ом;\n 6) Ф;\n 7) Тл;\n 8) Вб\n" << "Введите единицу измерения: " ;
    cin >> charin;

    switch(charin) {
        case(1):
            cout << "Число после перевода: " << intin/trans << " ед. СГСЭ" << endl;
            break;
        case(2):
            cout << "Число после перевода: " << intin * (pow(10, 5)) << " * 10^(-5) * Н" << endl;
            break;
        case(3):
            cout << "Число после перевода: " << intin * (pow(10, 7)) << " * 10^(-7) * Дж" << endl;
            break;
        case(4):
            cout << "Число после перевода: " << intin * (pow(10, 1)) << " * 10^(-1) * Па" << endl;
            break;
        case(5):
            cout << "Число после перевода: " << intin * (pow(10, 8)) << " * 10^(-8) * с*В" << endl;
            break;
        case(6):
            cout << "Число после перевода: " << intin * (pow(10, 9)) << " * 10^(-9) * с^2*Ом" << endl;
            break;
        case(7):
            cout << "Число после перевода: " << intin * (pow(10, -9)) << " * 10^9/c^2 * Ф" << endl;
            break;
        case(8):
            cout << "Число после перевода: " << intin * (pow(10, 4)) << " * 10^(-4) * с*Тл" << endl;
            break;
        default:
            cout << "Число после перевода: " << intin * (pow(10, 8)) << " * 10^(-8) * с*Вб" << endl;
    }

    return 0;
}