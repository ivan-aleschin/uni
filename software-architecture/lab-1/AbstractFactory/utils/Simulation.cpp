#include "Simulation.h"
#include <iostream>
#include "../factory/TaxiFactory.h"
#include "../factory/BusFactory.h"

void Simulation::dispatchPassengers(TransportFactory& factory, std::queue<Passenger>& passengers) {
    int vehiclesCount = 0;

    // Пока есть очередь из пассажиров
    while (!passengers.empty()) {
        // Запрашиваем у фабрики транспорт и водителя
        auto transport = factory.get_vehicle();
        auto driver = factory.get_driver();

        // Собираем их
        if (!transport->set_driver(driver)) {
            std::cout << "Failed to set driver!\n";
            break;
        }

        int boarded = 0;
        // Заполняем транспорт. Лимит контролируется самим транспортом!
        while (!passengers.empty()) {
            if (transport->add_passenger(passengers.front())) {
                passengers.pop();
                boarded++;
            } else {
                // Транспорт заполнен
                break;
            }
        }

        if (transport->is_ready_to_go()) {
            vehiclesCount++;
            std::cout << transport->get_type() << " #" << vehiclesCount 
                      << " is READY TO GO! (Boarded: " << boarded 
                      << ", Capacity: " << transport->get_places() << ")\n";
        } else {
            std::cout << transport->get_type() << " is NOT READY!\n";
            break;
        }
    }
}

void Simulation::dispatchPizza(PizzaFactory& factory, std::queue<PizzaBox>& boxes) {
    int vansCount = 0;

    while (!boxes.empty()) {
        auto van = factory.get_vehicle();
        auto driver = factory.get_driver();

        if (!van->set_driver(driver)) {
            std::cout << "Failed to set driver for pizza van!\n";
            break;
        }

        int loaded = 0;
        while (!boxes.empty()) {
            if (van->add_box(boxes.front())) {
                boxes.pop();
                loaded++;
            } else {
                break;
            }
        }

        if (van->is_ready_to_deliver()) {
            vansCount++;
            std::cout << van->get_type() << " #" << vansCount 
                      << " is READY TO DELIVER! (Loaded: " << loaded 
                      << ", Capacity: " << van->get_places() << ")\n";
        } else {
            std::cout << van->get_type() << " is NOT READY!\n";
            break;
        }
    }
}

void Simulation::runAll() {
    std::cout << "--- Симуляция работы Такси ---\n";
    std::queue<Passenger> queueForTaxi;
    for (int i = 0; i < 20; ++i) queueForTaxi.push(Passenger());
    
    TaxiFactory taxiFactory;
    dispatchPassengers(taxiFactory, queueForTaxi);

    std::cout << "\n--- Симуляция работы Автобуса ---\n";
    std::queue<Passenger> queueForBus;
    for (int i = 0; i < 30; ++i) queueForBus.push(Passenger());
    
    BusFactory busFactory;
    dispatchPassengers(busFactory, queueForBus);

    std::cout << "\n--- Симуляция доставки пиццы ---\n";
    std::queue<PizzaBox> boxes;
    for (int i = 1; i <= 25; ++i) boxes.push(PizzaBox(i));
    
    ConcretePizzaFactory pizzaFactory;
    dispatchPizza(pizzaFactory, boxes);
}
