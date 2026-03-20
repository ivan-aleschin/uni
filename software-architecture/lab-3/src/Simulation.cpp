#include "Simulation.h"
#include "Airplane.h"
#include <iostream>

void Simulation::runDemo() {
    std::cout << "=== СИСТЕМА КОНТРОЛЯ ЗАГРУЗКИ САМОЛЕТА (COMPOSITE) ===\n\n";

    // Создаем самолет с максимальной допустимой загрузкой багажа 3500 кг
    Airplane plane(3500);

    // Сборка экипажа и пассажиров
    plane.assembleCrewAndPassengers();

    // Вывод начальной карты загрузки
    plane.printLoadingMap();

    // Демонстрация удаления пассажира (дополнительная проверка структуры)
    std::cout << "\n--- Демонстрация удаления пассажира ---\n";
    std::string victim = "Alice_Brown";
    if (plane.removePassenger(victim)) {
        std::cout << "Пассажир удалён с рейса: " << victim << "\n";
    } else {
        std::cout << "Пассажир не найден: " << victim << "\n";
    }

    // Вывод обновленной карты загрузки после удаления пассажира
    plane.printLoadingMap();
    
    std::cout << "\n=== РАБОТА ЗАВЕРШЕНА ===\n";
}