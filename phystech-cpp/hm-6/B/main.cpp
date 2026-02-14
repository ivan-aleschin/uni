#include <iostream>
#include "windows.h"

#include "Number.h"

int main() {
    SetConsoleOutputCP(CP_UTF8);

    int tmp{0};
    Number d1;
    Number d2;
    std::cout << "Введите числитель первой дроби: " << std::endl;
    std::cin >> tmp;
    d1.setNum(tmp);
    std::cout << "Введите знаменатель первой дроби: " << std::endl;
    std::cin >> tmp;
    d1.setDenom(tmp);
    std::cout << "Введите числитель второй дроби: " << std::endl;
    std::cin >> tmp;
    d2.setNum(tmp);
    std::cout << "Введите знаменатель второй дроби: " << std::endl;
    std::cin >> tmp;
    d2.setDenom(tmp);

    Number sum = d1 + d2;
    Number minus = d1 - d2;
    Number multi = d1 * d2;
    Number div = d1 / d2;
    Number com = d1 < d2;
    sum.reduction();
    minus.reduction();
    multi.reduction();
    div.reduction();
    com.reduction();

    std::cout << "Сумма: " << sum.getNum() << "/" << sum.getDenom() << std::endl;
    std::cout << "Разность: " << minus.getNum() << "/" << minus.getDenom() << std::endl;
    std::cout << "Умножение: " << multi.getNum() << "/" << multi.getDenom() << std::endl;
    std::cout << "Деление: " << div.getNum() << "/" << div.getDenom() << std::endl;
    std::cout << "Дробь " << com.getNum() << "/" << com.getDenom() << " больше" << std::endl;

    return 0;
}