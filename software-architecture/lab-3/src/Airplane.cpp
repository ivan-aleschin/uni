#include "../include/Airplane.h"
#include "../include/FirstClass.h"
#include "../include/BusinessClass.h"
#include "../include/EconomyClass.h"
#include "../include/Passenger.h"
#include "../include/CrewMember.h"
#include <iostream>

Airplane::Airplane(int maxLoad) : maxBaggageLoad(maxLoad) {}

Airplane::~Airplane() {
    for (auto c : components) delete c;
}

void Airplane::add(Component* c) {
    if (c) components.push_back(c);
}

int Airplane::getBaggageWeight() const {
    int total = 0;
    for (const auto& c : components) total += c->getBaggageWeight();
    return total;
}

bool Airplane::removePassenger(const std::string& name) {
    for (auto c : components) {
        if (c->removePassenger(name)) return true;
    }
    return false;
}

void Airplane::assembleCrewAndPassengers() {

    add(new Pilot("Pilot_1"));
    add(new Pilot("Pilot_2"));
    for (int i = 1; i <= 6; ++i) {
        add(new Stewardess("Stewardess_" + std::to_string(i)));
    }


    auto* first = new FirstClass();
    first->add(new Passenger("John_Doe", 25));
    first->add(new Passenger("Jane_Smith", 40));
    first->add(new Passenger("Alice_Brown", 15));
    first->add(new Passenger("Bob_Wilson", 50));
    first->add(new Passenger("Carol_Davis", 30));
    add(first);


    auto* bus = new BusinessClass();
    for (int i = 1; i <= 15; ++i) {
        int bag = 20 + i * 2; 
        bus->add(new Passenger("BusPass_" + std::to_string(i), bag));
    }
    add(bus);


    auto* eco = new EconomyClass();
    for (int i = 1; i <= 100; ++i) {
        int bag = 20 + (i % 41); 
        eco->add(new Passenger("EcoPass_" + std::to_string(i), bag));
    }
    add(eco);

    adjustBaggageLoad();
}

void Airplane::adjustBaggageLoad() {
    int current = getBaggageWeight();
    if (current <= maxBaggageLoad) {
        removedBaggages.clear();
        return;
    }

    int excess = current - maxBaggageLoad;
    removedBaggages.clear();

    for (auto c : components) {
        EconomyClass* eco = dynamic_cast<EconomyClass*>(c);
        if (eco) {
            eco->offloadExcessBaggage(excess, removedBaggages);
            if (excess <= 0) break;
        }
    }
}

void Airplane::printLoadingMap() const {
    std::cout << "=== Карта загрузки самолёта ===\n\n";

    std::cout << "Экипаж:\n";
    int pilots = 0, stewards = 0;
    for (const auto& c : components) {
        if (dynamic_cast<const Pilot*>(c)) pilots++;
        else if (dynamic_cast<const Stewardess*>(c)) stewards++;
    }
    std::cout << "  Пилотов: " << pilots << "\n";
    std::cout << "  Стюардесс: " << stewards << "\n";
    std::cout << "  Всего экипажа: " << (pilots + stewards) << "\n\n";

    for (const auto& c : components) {
        if (auto* sec = dynamic_cast<const Section*>(c)) {
            sec->printLoadingMap();
            std::cout << std::endl;
        }
    }

    int total = getBaggageWeight();
    std::cout << "Общий багаж: " << total << " кг\n";
    std::cout << "Максимально допустимо: " << maxBaggageLoad << " кг\n";
    std::cout << "Состояние: " << (total > maxBaggageLoad ? "ПЕРЕГРУЗ!" : "В норме") << "\n\n";

    std::cout << "Снятие багажа:\n";
    if (removedBaggages.empty()) {
        std::cout << "  Багаж не снимался.\n";
    } else {
        std::cout << "  Снято у пассажиров эконом-класса:\n";
        for (const auto& r : removedBaggages) {
            std::cout << "    - " << r.first << ": " << r.second << " кг\n";
        }
    }
    std::cout << "================================\n";
}