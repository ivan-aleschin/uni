#include <iostream>
#include <numeric>

#include "Header.hpp"

namespace Rat {
	Rational::Rational(int num, unsigned int den) :numerate(num), denominator(den) {
		if (!den) {
			denominator = 1;
			std::cout << "Error: division by zero. Your number was converted to " << numerate;
		}
		reduct();
	}

	void Rational::reduct() {
		int temp = numerate;
		numerate /= std::gcd(denominator, numerate);
		denominator /= std::gcd(denominator, temp);
	}
	void Rational::set_num_and_den(int num, unsigned int den) {
		numerate = num;
		denominator = den;
	}
	int Rational::get_num() {
		return numerate;
	}
	int Rational::get_den() {
		return denominator;
	}

	std::ostream& operator<< (std::ostream& stream, const Rational& number) {
		stream << number.numerate << "/" << number.denominator;
		return stream;
	}
	std::istream& operator>> (std::istream& stream, Rational& number) {
		int d;
		stream >> number.numerate >> d;
		if (!d) {
			number.denominator = d;
		}
		else {
			number.denominator = 1;
			std::cout << "Error: division by zero. Your number was converted to " << number.numerate;
		}
		number.reduct();
		return stream;
	}

	Rational& Rational::operator+=(const Rational& number) {
		unsigned int temp = denominator;
		denominator *= number.denominator;
		numerate = numerate * number.denominator + temp * number.numerate;
		this->reduct();
		return *this;
	}
	Rational& Rational::operator-=(const Rational& number) {
		unsigned int temp = denominator;
		denominator *= number.denominator;
		numerate = numerate * number.denominator - temp * number.numerate;
		this->reduct();
		return *this;
	}
	Rational& Rational::operator*=(const Rational& number) {
		denominator *= number.denominator;
		numerate *= number.numerate;
		this->reduct();
		return *this;
	}
	Rational& Rational::operator/=(const Rational& number) {
		denominator *= number.numerate;
		numerate *= number.denominator;
		this->reduct();
		return *this;
	}
	
	Rational operator+ (const Rational& first, const Rational& second) {
		Rational result;
		result.denominator = first.denominator * second.denominator;
		result.numerate = first.numerate * second.denominator + first.denominator * second.numerate;
		result.reduct();
		return result;
	}
	Rational operator-(const Rational& first, const Rational& second) {
		Rational result;
		result.denominator = first.denominator * second.denominator;
		result.numerate = first.numerate * second.denominator - first.denominator * second.numerate;
		result.reduct();
		return result;
	}
	Rational operator*(const Rational& first, const Rational& second) {
		Rational result;
		result.denominator = first.denominator * second.denominator;
		result.numerate = first.numerate * second.numerate;
		result.reduct();
		return result;
	}
	Rational operator/(const Rational& first, const Rational& second) {
		Rational result;
		result.denominator = first.denominator * second.numerate;
		result.numerate = first.numerate * second.denominator;
		if (!result.denominator)
		{
			result.denominator = 1;
			std::cout << "Error: division by zero. Your number was converted to " << result.numerate;
		}
		result.reduct();
		return result;
	}

	Rational& Rational::operator++() {
		this->numerate += denominator; 
		return *this;
	}
	Rational& Rational::operator--() {
		this->numerate-=denominator;
		return *this;
	}
	Rational Rational::operator++(int) {
		Rational temp = *this;
		this->numerate += denominator;
		return temp;
	}
	Rational Rational::operator--(int) {
		Rational temp = *this;
		this -> numerate-=denominator;
		return temp;
	}

	bool operator==(const Rational& first, const Rational& second) {
		return (first - second).numerate == 0;
	}
	bool operator>(const Rational& first, const Rational& second) {
		return (first - second).numerate > 0;
	}
	bool operator<(const Rational& first, const Rational& second) {
		return (first - second).numerate < 0;
	}
	bool operator>=(const Rational& first, const Rational& second) {
		return (first - second).numerate >= 0;
	}
	bool operator<=(const Rational& first, const Rational& second) {
		return (first - second).numerate <= 0;
	}
	bool operator!=(const Rational& first, const Rational& second) {
		return !((first - second).numerate == 0);
	}
}