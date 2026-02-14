#include <iostream>
#include <algorithm>
#include "Person.hpp"

void Person::a()
{
	std::cout << "Hello!" << '\n'; 
	//Выводит ошибку многократно определенного внешнего символа, функция-член a() определена и в двух файлах Source.cpp и person.cpp, чтобы исправить необходимо выбрать только одно определение функции a()
	
}

int main()
{
	Person p(1);
	p.a();
	p.b();

	return 0;
}