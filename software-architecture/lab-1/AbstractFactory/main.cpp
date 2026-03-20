#include "utils/Simulation.h"
#include <iostream>

int main() {
    std::cout << "--- Симуляция работы Такси ---\n";
    Simulation::runTaxiDemo();

    std::cout << "\n--- Симуляция работы Автобуса ---\n";
    Simulation::runBusDemo();

    std::cout << "\n--- Симуляция доставки пиццы ---\n";
    Simulation::runPizzaDemo();

    return 0;
}
