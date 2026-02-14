#include <string>
#include <vector>
#include <iostream>
#include <windows.h>
#include <cctype>

using namespace std;

int fi(int &number, int &tmp1, int &tmp2){
    if (number == 1){
        return 0;
    } else{
        number--;
        int tmp{0};
        tmp = tmp2;
        tmp2 += tmp1;
        tmp1 = tmp;
        fi(number, tmp1, tmp2);
        return 0;
    }
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    //setlocale(LC_ALL,"rus");
    //SetConsoleCP(1251);
    //SetConsoleOutputCP(1251);
    int number{0}, tmp1{0}, tmp2{1};
    cout << "Введите номер искомого числа Фибоначчи(начинается с 1): " << endl;
    cin >> number;

    if(number == 1){
        cout << "Искомое число Фибоначчи: " << 1;
    } else{
        fi(number, tmp1, tmp2);
        cout << "Искомое число Фибоначчи: " << tmp2;
    }

    return 0;
}