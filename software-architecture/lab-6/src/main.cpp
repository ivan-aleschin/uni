#include "DeansOffice.h"
#include "Department.h"
#include "Teacher.h"

#include <iostream>
#include <vector>

int main() {
    Department department("Программная инженерия");
    DeansOffice dean(department);

    Teacher ivanov("Иванов И.И.", "Архитектура ПО");
    Teacher petrov("Петров П.П.", "Архитектура ПО");
    Teacher sidorov("Сидоров С.С.", "Архитектура ПО");

    dean.watch(ivanov);
    dean.watch(petrov);
    dean.watch(sidorov);

    std::vector<Teacher*> teachers{&ivanov, &petrov, &sidorov};

    std::cout << "--- Неделя 1: все преподаватели подали успеваемость ---\n";
    ivanov.submitGrades("PI-31", 1);
    petrov.submitGrades("PI-31", 1);
    sidorov.submitGrades("PI-31", 1);
    dean.checkWeek(1, teachers);

    std::cout << "\n--- Неделя 2: Петров не подал успеваемость ---\n";
    ivanov.submitGrades("PI-31", 2);
    sidorov.submitGrades("PI-31", 2);
    dean.checkWeek(2, teachers);

    std::cout << "\n--- Неделя 3: Иванов и Петров не подали успеваемость ---\n";
    sidorov.submitGrades("PI-31", 3);
    dean.checkWeek(3, teachers);

    return 0;
}
