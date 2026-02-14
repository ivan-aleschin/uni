#include <iostream>
#include <windows.h>
#include <iomanip>
#include <cmath>

int main() {
    using namespace std;
    SetConsoleOutputCP(CP_UTF8);

    double a, b, c, d;
    cout << "Введите a: " << endl;
    cin >> a;
    cout << "Введите b: " << endl;
    cin >> b;
    cout << "Введите c: " << endl;
    cin >> c;
    cout << "\n";

    d = (b*b - 4*a*c);
    if (a == 0) {
        cout << "Найдено одно решение: " << -c/b << endl;
    } else if(d > 0) {
        cout << "Найдено два решения: " << (-b + sqrt(d)) / (2 * a) << " " << (-b - sqrt(d)) / (2 * a) << endl;
    } else if(d == 0) {
        cout << "Найдено одно решение: " << (-b) / (2 * a) << endl;
    } else {
        cout << "Решений нет((" << endl;
    }

    return 0;
}