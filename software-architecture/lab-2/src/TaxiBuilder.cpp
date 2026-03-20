#include "../include/TaxiBuilder.h"
#include "../include/Taxi.h"
#include "../include/Driver.h"
#include "../include/Passenger.h"
#include <iostream>

TaxiBuilder::TaxiBuilder() { 
    reset(); 
}

void TaxiBuilder::reset() { 
    taxi = std::make_unique<Taxi>(); 
}

void TaxiBuilder::setDriver(const std::string& name, const std::string& category) {
    if (!taxi) {
        std::cerr << "Ошибка: taxi не инициализирован\n";
        return;
    }
    
    if (category != "B") {
        std::cout << "Ошибка: Водитель такси должен иметь категорию B\n";
        return;
    }
    
    auto driver = std::make_unique<Driver>(name, category);
    if (taxi->setDriver(std::move(driver))) {
        std::cout << "  ✓ Водитель " << name << " назначен\n";
    }
}

bool TaxiBuilder::tryAddPassenger(std::unique_ptr<Passenger> passenger, bool silent) {
    if (!passenger || !taxi) return false;
    
    if (!taxi->addPassenger(std::move(passenger))) {
        if (!silent) std::cout << "Ошибка: Такси заполнено\n";
        return false;
    }
    return true;
}

void TaxiBuilder::addPassenger(const std::string& type, bool needsSafety) {
    if (!taxi) {
        std::cerr << "Ошибка: taxi не инициализирован\n";
        return;
    }
    
    std::unique_ptr<Passenger> passenger;
    if (type == "adult") {
        passenger = std::make_unique<AdultPassenger>();
    } else if (type == "child") {
        passenger = std::make_unique<ChildPassenger>(needsSafety);
    } else {
        std::cout << "Ошибка: В такси можно только adult или child\n";
        return;
    }
    
    tryAddPassenger(std::move(passenger), false);
}

std::vector<std::unique_ptr<Passenger>> 
TaxiBuilder::tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) {
    std::vector<std::unique_ptr<Passenger>> rejected;
    
    if (!taxi) return rejected;
    
    for (auto& p : candidates) {
        if (!tryAddPassenger(std::move(p), true)) {
            rejected.push_back(std::move(p));
        }
    }
    
    return rejected;
}

std::unique_ptr<Vehicle> TaxiBuilder::build() { 
    return std::move(taxi); 
}