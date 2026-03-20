#include "../include/BusBuilder.h"
#include "../include/Bus.h"
#include "../include/Driver.h"
#include "../include/Passenger.h"
#include <iostream>

BusBuilder::BusBuilder() { reset(); }

void BusBuilder::reset() { bus = std::make_unique<Bus>(); }

void BusBuilder::setDriver(const std::string& name, const std::string& category) {
    if (category != "D") {
        std::cout << "Ошибка: Водитель автобуса должен иметь категорию D\n";
        return;
    }
    bus->setDriver(std::make_unique<Driver>(name, category));
    std::cout << "  ✓ Водитель " << name << " назначен\n";
}

bool BusBuilder::tryAddPassenger(std::unique_ptr<Passenger> passenger, bool silent) {
    if (!passenger) return false;
    
    if (!bus->addPassenger(std::move(passenger))) {
        if (!silent) std::cout << "Ошибка: Автобус заполнен\n";
        return false;
    }
    return true;
}

void BusBuilder::addPassenger(const std::string& type, bool /*needsSafety*/) {
    std::unique_ptr<Passenger> passenger;
    if (type == "adult") {
        passenger = std::make_unique<AdultPassenger>();
    } else if (type == "benefit") {
        passenger = std::make_unique<BenefitPassenger>();
    } else if (type == "child") {
        passenger = std::make_unique<ChildPassenger>(false);
    } else {
        std::cout << "Ошибка: Неизвестный тип пассажира\n";
        return;
    }
    tryAddPassenger(std::move(passenger), false);
}

std::vector<std::unique_ptr<Passenger>> 
BusBuilder::tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) {
    std::vector<std::unique_ptr<Passenger>> rejected;
    int added = 0;
    
    for (auto& p : candidates) {
        if (tryAddPassenger(std::move(p), true)) {
            added++;
        } else {
            rejected.push_back(std::move(p));
        }
    }
    
    if (added > 0) {
        std::cout << "  ✓ Посажено в автобус: " << added 
                  << ", отвергнуто: " << rejected.size() << "\n";
    }
    return rejected;
}

std::unique_ptr<Vehicle> BusBuilder::build() { return std::move(bus); }