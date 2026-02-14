#pragma once

namespace Rat {
	class Rational {
	private:
		int numerate;
		unsigned int denominator;
	public:
		Rational() :numerate(0), denominator(1) {};
		Rational(int num, unsigned int den);
		Rational(int num) :numerate(num), denominator(1) {};
		Rational(double number) :numerate(number * 1e6), denominator(1e6) { reduct(); }

		void reduct();
		void set_num_and_den(int num, unsigned int den);
		int get_num();
		int get_den();

		friend std::ostream& operator<< (std::ostream& stream, const Rational& number);
		friend std::istream& operator>> (std::istream& stream, Rational& number);

		Rational& operator+=(const Rational& number);
		Rational& operator-=(const Rational& number);
		Rational& operator*=(const Rational& number);
		Rational& operator/=(const Rational& number);

		friend Rational operator+(const Rational& first, const Rational& second);
		friend Rational operator-(const Rational& first, const Rational& second);
		friend Rational operator*(const Rational& first, const Rational& second);
		friend Rational operator/(const Rational& first, const Rational& second);

		Rational& operator++();
		Rational& operator--();
		Rational operator++(int);
		Rational operator--(int);

		explicit operator double() const {
			return static_cast<double>(numerate) / static_cast<double>(denominator);
		};
		explicit operator bool() const {
			return static_cast<bool>(numerate);
		};

		friend bool operator==(const Rational& first, const Rational& second);
		friend bool operator>(const Rational& first, const Rational& second);
		friend bool operator<(const Rational& first, const Rational& second);
		friend bool operator>=(const Rational& first, const Rational& second);
		friend bool operator<=(const Rational& first, const Rational& second);
		friend bool operator!=(const Rational& first, const Rational& second);
	};
}
