#include <iostream>
#include "Header.hpp"

int main() {
    Rat::Rational number;
    try {
        number.set_num_and_den (1, 2);
    } catch(const std::invalid_argument& e) {
        std::cout << e.what();
    }
    std::cout << number << " = " << double(number) << "; " << bool(number) << '\n';

    Rat::Rational number1;
    try {
        number1.set_num_and_den(2, 0);
    } catch(const std::invalid_argument& e) {
        std::cout << e.what();
    }
    std::cout<<"Numerate: " << number.get_num() << "; Denominator: " << number.get_den()<<std::endl;

    std::cout << number1 << " - " << number << " = " << number1 - number << std::endl;
    std::cout << number1 << " + " << number << " = " << number1 + number << std::endl;
    std::cout << number1 << " * " << number << " = " << number1 * number << std::endl;
    try {
        Rat::Rational res = number1 / number;
        std::cout << number1 << " / " << number << " = " << res << std::endl;
    } catch(const std::invalid_argument& e) {
        std::cout << e.what();
    }

    number += 2;
    std::cout << number << " - " << 2 << " = " << number - 2 << std::endl;

    number1--;
    std::cout << number1 << " - " << 1 << " = " << number1 - 1 << std::endl;

    if (number1 >= number) {
        std::cout << number1 << " - " << number << " >= 0 ";
    }
    else {
        std::cout << number1 << " - " << number << " < 0 ";
    }

    return 0;
}