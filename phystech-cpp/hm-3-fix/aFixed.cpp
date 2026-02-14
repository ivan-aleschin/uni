#include <string>
#include <vector>
#include <iostream>
#include <windows.h>
#include <cctype>

using namespace std;

int fi(int number) {
    if ((number == 1) || (number == 2)) {
        return 1;
    }

    return fi(number-1) + fi(number-2);
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    //setlocale(LC_ALL,"rus");
    //SetConsoleCP(1251);
    //SetConsoleOutputCP(1251);
    int number{0};
    cout << "Введите номер искомого числа Фибоначчи(начинается с 1): " << endl;
    cin >> number;

    cout << "Искомое число Фибоначчи: " << endl;
    cout << fi(number);

    return 0;
}