#include "DeansOffice.h"
#include "Department.h"
#include "Teacher.h"

#include <iostream>
#include <vector>

int main() {
    Department department("Программная инженерия");
    DeansOffice dean(department);

    // Один факультет, одна дисциплина «Архитектура ПО», три группы.
    // Каждый преподаватель ведёт свою группу.
    Teacher ivanov("Иванов И.И.", "Архитектура ПО");
    Teacher petrov("Петров П.П.", "Архитектура ПО");
    Teacher sidorov("Сидоров С.С.", "Архитектура ПО");

    dean.watch(ivanov);
    dean.watch(petrov);
    dean.watch(sidorov);

    std::vector<Teacher*> teachers{&ivanov, &petrov, &sidorov};

    std::cout << "--- Неделя 1: все преподаватели подали успеваемость по своим группам ---\n";
    ivanov.submitGrades("PI-31", 1);
    petrov.submitGrades("PI-32", 1);
    sidorov.submitGrades("PI-33", 1);
    dean.checkWeek(1, teachers);

    std::cout << "\n--- Неделя 2: Петров (группа PI-32) не подал успеваемость ---\n";
    ivanov.submitGrades("PI-31", 2);
    sidorov.submitGrades("PI-33", 2);
    dean.checkWeek(2, teachers);

    std::cout << "\n--- Неделя 3: Иванов (PI-31) и Петров (PI-32) не подали успеваемость ---\n";
    sidorov.submitGrades("PI-33", 3);
    dean.checkWeek(3, teachers);

    std::cout << "\n--- Неделя 4: Сидоров уходит на кафедру — деканат снимает наблюдение ---\n";
    dean.unwatch(sidorov);
    std::vector<Teacher*> remainingTeachers{&ivanov, &petrov};

    // Иванов сдал. Петров и Сидоров — нет.
    // Сидоров больше не в списке наблюдения, поэтому деканат его не штрафует.
    ivanov.submitGrades("PI-31", 4);
    dean.checkWeek(4, remainingTeachers);

    return 0;
}
