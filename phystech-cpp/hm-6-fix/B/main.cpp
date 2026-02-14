#include <iostream>
#include "Header.hpp"

int main() {
	Rat::Rational number(1, 2);
	std::cout << number << " = " << double(number) << "; " << bool(number) << '\n';
	
	Rat::Rational number1;
	number1.set_num_and_den(2, 3);
	std::cout<<"Numerate: " << number.get_num() << "; Denominator: " << number.get_den()<<std::endl;
	
	std::cout << number1 << " - " << number << " = " << number1 - number << std::endl;
	std::cout << number1 << " + " << number << " = " << number1 + number << std::endl;
	std::cout << number1 << " * " << number << " = " << number1 * number << std::endl;
	std::cout << number1 << " / " << number << " = " << number1 / number << std::endl;

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