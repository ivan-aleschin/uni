#include <vector>
#include <iostream>
#include <windows.h>
#include <string>
#include "Energy.h"

using namespace std;

int main()
{
    SetConsoleOutputCP(CP_UTF8);

    int tmp;
    double x;
    Energy ad;
    cout << "1) Электронвольты 2) Эрги 3) Джоули" << endl;
    cout << "Выберите единицу измерения для ввода (1-3): " << endl;
    cin >> tmp;
    cout << "Введите число: " << endl;
    cin >> x;

    switch(tmp){
        case 1:
            ad.setInput1(x);
            break;
        case 2:
            ad.setInput2(x);
            break;
        case 3:
            ad.setInput3(x);
            break;
    }

    cout << "1) Электронвольты 2) Эрги 3) Джоули" << endl;
    cout << "Выюерите единицу измерения для вывода (1-3): " << endl;
    cin >> tmp;
    cout << "Переведенное число: " << endl;
    switch(tmp){
        case 1:
            cout << ad.getOutput1() << endl;
            break;
        case 2:
            cout << ad.getOutput2() << endl;
            break;
        case 3:
            cout << ad.getOutput3() << endl;
            break;
    }

    return 0;
}