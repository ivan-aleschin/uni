#include "Simulation.h"
#include <iostream>
#include <vector>
#include <queue>
#include <memory>

#include "../factory/PizzaFactory.h"
#include "../factory/TaxiFactory.h"
#include "../factory/BusFactory.h"
#include "../core/PizzaBox.h"
#include "../core/Passenger.h"
#include "../core/Vehicle.h"

namespace {
    void printStatus(const std::shared_ptr<Vehicle>& v) {
        std::cout << v->getType() << ": ";
        if (v->isReadyToGo()) std::cout << "READY TO GO\n";
        else std::cout << "NOT READY\n";
    }
}

void Simulation::runTaxiDemo() {
    std::cout << "=== TAXI QUEUE DEMO ===\n";
    std::cout << "Creating 20 passengers in queue...\n\n";

    std::queue<Passenger> passengerQueue;
    for (int i = 0; i < 20; ++i) {
        passengerQueue.push(Passenger());
    }
    std::cout << "Queue size: " << passengerQueue.size() << " passengers\n\n";

    TaxiFactory taxiFactory;
    int taxiCount = 0;
    std::vector<std::shared_ptr<Vehicle>> taxis;

    while (!passengerQueue.empty()) {
        std::vector<Passenger> passengerForTaxi;
        const int TAXI_CAPACITY = 4;

        for (int i = 0; i < TAXI_CAPACITY && !passengerQueue.empty(); ++i) {
            passengerForTaxi.push_back(passengerQueue.front());
            passengerQueue.pop();
        }

        std::vector<Passenger> notSeated;
        auto taxi = taxiFactory.createVehicle(passengerForTaxi, notSeated);

        if (taxi) {
            ++taxiCount;
            taxis.push_back(taxi);
            std::cout << "Taxi #" << taxiCount << " created with " 
                      << passengerForTaxi.size() << " passengers\n";
            printStatus(taxi);
        } else {
            std::cout << "Failed to create taxi. Not seated: " << notSeated.size() << "\n";
            for (const auto& p : notSeated) {
                passengerQueue.push(p);
            }
        }
    }

    std::cout << "\n=== SUMMARY ===\n";
    std::cout << "Total taxis created: " << taxiCount << "\n";
    std::cout << "Passengers remaining in queue: " << passengerQueue.size() << "\n\n";
}

void Simulation::runBusDemo() {
    std::cout << "=== BUS FACTORY ===\n";
    BusFactory busFactory;
    std::vector<Passenger> busPs(30);
    std::vector<Passenger> notSeated;

    auto bus = busFactory.createVehicle(busPs, notSeated);
    if (bus) {
        std::cout << "Bus created with 30 passengers\n";
        printStatus(bus);
    } else {
        std::cout << "Bus creation failed\n";
    }
    std::cout << "\n";
}

void Simulation::runPizzaDemo() {
    std::cout << "=== PIZZA DELIVERY DEMO ===\n";
    std::cout << "Creating 25 pizza boxes for delivery...\n\n";

    std::vector<PizzaBox> pizzaBoxes;
    for (int i = 1; i <= 25; ++i) {
        pizzaBoxes.push_back(PizzaBox(i));
    }

    PizzaFactory pizzaFactory;
    std::vector<PizzaBox> remainingBoxes = pizzaBoxes;
    int deliveryCount = 0;

    while (!remainingBoxes.empty()) {
        std::vector<PizzaBox> boxesForVan;
        const size_t VAN_CAPACITY = 10;

        for (size_t i = 0; i < VAN_CAPACITY && !remainingBoxes.empty(); ++i) {
            boxesForVan.push_back(remainingBoxes.back());
            remainingBoxes.pop_back();
        }

        std::vector<PizzaBox> notDelivered;
        auto van = pizzaFactory.createDelivery(boxesForVan, notDelivered);

        if (van) {
            ++deliveryCount;
            std::cout << "Pizza Van #" << deliveryCount << " created with " 
                      << van->getBoxCount() << " boxes\n";
            std::cout << "  Type: " << van->getType() << ", Ready: " 
                      << (van->isReadyToDeliver() ? "YES" : "NO") << "\n";
        } else {
            std::cout << "Failed to create pizza van. Undelivered: " << notDelivered.size() << "\n";
            for (const auto& box : notDelivered) {
                remainingBoxes.push_back(box);
            }
        }
    }

    std::cout << "\n=== PIZZA DELIVERY SUMMARY ===\n";
    std::cout << "Total pizza vans created: " << deliveryCount << "\n";
    std::cout << "Remaining boxes: " << remainingBoxes.size() << "\n";
}

void Simulation::runAll() {
    runTaxiDemo();
    runBusDemo();
    runPizzaDemo();
}