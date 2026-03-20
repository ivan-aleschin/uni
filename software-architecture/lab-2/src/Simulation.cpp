#include "Simulation.h"
#include <iostream>
#include "Director.h"
#include "BusBuilder.h"
#include "TaxiBuilder.h"
#include "BoatBuilder.h"

void Simulation::runTaxiDemo() {
    Director director;
    TaxiBuilder taxiBuilder;
    taxiBuilder.setChildSeat(true);
    director.setBuilder(&taxiBuilder);
    try {
        director.constructTaxiWithFamily();
        auto taxi = taxiBuilder.build();
        std::cout << "✓ Успешно: " << taxi->getType() 
                  << " | Пассажиров: " << taxi->getPassengerCount() << "/4\n";
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка: " << e.what() << "\n";
    }
}

void Simulation::runBoatDemo() {
    Director director;
    BoatBuilder boatBuilder;
    director.setBuilder(&boatBuilder);
    try {
        director.constructBoatWithTourists();
        auto boat = boatBuilder.build();
        std::cout << "✓ Успешно: " << boat->getType() 
                  << " | Пассажиров: " << boat->getPassengerCount() << "/6\n";
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка: " << e.what() << "\n";
    }
}

void Simulation::runBusDemo() {
    BusBuilder busBuilder;
    busBuilder.setDriver("Водитель Автобуса", "D");
    try {
        auto bus = busBuilder.build();
        std::cout << "✓ Успешно: " << bus->getType() 
                  << " | Пассажиров: " << bus->getPassengerCount() << "/30\n";
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка (ожидаемо, так как нет пассажиров): " << e.what() << "\n";
    }
}