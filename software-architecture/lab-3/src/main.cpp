#include "../include/Airplane.h"
#include <iostream>

int main() {
    Airplane plane(3500);

    plane.assembleCrewAndPassengers();

    plane.printLoadingMap();

    std::cout << "\n--- Демонстрация удаления пассажира ---\n";
    std::string victim = "Bob_Wilson";
    if (plane.removePassenger(victim)) {
        std::cout << "Пассажир удалён: " << victim << "\n\n";
    } else {
        std::cout << "Пассажир не найден: " << victim << "\n\n";
    }

    plane.printLoadingMap();

    return 0;
}
