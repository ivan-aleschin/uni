#include "Simulation.h"
#include <iostream>

int main() {
    std::cout << "=== СИСТЕМА КОНТРОЛЯ ТРАНСПОРТА (BUILDER) ===\n\n";

    std::cout << "--- 1. Создание Такси (с детским креслом) ---\n";
    Simulation::runTaxiDemo();

    std::cout << "\n--- 2. Создание Надувной Лодки (со спасательными жилетами) ---\n";
    Simulation::runBoatDemo();

    std::cout << "\n--- 3. Создание Автобуса (через Builder) ---\n";
    Simulation::runBusDemo();

    std::cout << "\n=== РАБОТА ЗАВЕРШЕНА ===\n";

    return 0;
}