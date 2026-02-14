#include <iostream>
#include <windows.h>
#include <iomanip>
#include <cmath>

int main() {
    using namespace std;
    SetConsoleOutputCP(CP_UTF8);

    double x, y;
    cout << "Введите первую переменную для обмена: " << endl;
    cin >> x;
    cout << "Введите вторую переменную для обмена: " << endl;
    cin >> y;

    x += y;
    y -= x;
    y = -y;
    x -= y;

    cout << "Первая переменная: " << x << "\nВторая переменная: " << y << endl;

    return 0;
}