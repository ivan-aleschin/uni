#include "../include/BoatBuilder.h"
#include "../include/InflatableBoat.h"
#include "../include/Driver.h"
#include "../include/Passenger.h"
#include <iostream>

BoatBuilder::BoatBuilder() { 
    reset(); 
}

void BoatBuilder::reset() { 
    boat = std::make_unique<InflatableBoat>(); 
}

void BoatBuilder::setDriver(const std::string& name, const std::string& category) {
    if (!boat) return;
    
    if (category != "B" && category != "D") {
        std::cout << "Ошибка: Для лодки нужны права категории B или D\n";
        return;
    }
    
    auto driver = std::make_unique<Driver>(name, category);
    if (boat->setDriver(std::move(driver))) {
        std::cout << "  ✓ Капитан " << name << " назначен\n";
    }
}

bool BoatBuilder::tryAddPassenger(std::unique_ptr<Passenger> passenger, bool silent) {
    if (!passenger || !boat) return false;
    
    passenger->setNeedsSafetyEquipment(true);
    
    if (boat->getAvailableLifeJackets() <= 0) {
        if (!silent) std::cout << "  ✗ Нет свободных спасательных жилетов\n";
        return false;
    }
    
    if (!boat->addPassenger(std::move(passenger))) {
        if (!silent) std::cout << "  ✗ Лодка заполнена\n";
        return false;
    }
    
    if (!silent) {
        std::cout << "  ✓ Пассажир посажен в лодку (осталось жилетов: " 
                  << boat->getAvailableLifeJackets() << ")\n";
    }
    return true;
}

void BoatBuilder::addPassenger(const std::string& type, bool needsSafety) {
    if (!boat) return;
    
    std::unique_ptr<Passenger> passenger;
    if (type == "adult") {
        passenger = std::make_unique<AdultPassenger>();
    } else if (type == "child") {
        passenger = std::make_unique<ChildPassenger>(needsSafety);
    } else if (type == "benefit") {
        passenger = std::make_unique<BenefitPassenger>();
    } else {
        std::cout << "Ошибка: Неизвестный тип пассажира\n";
        return;
    }
    
    tryAddPassenger(std::move(passenger), false);
}

std::vector<std::unique_ptr<Passenger>> 
BoatBuilder::tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) {
    std::vector<std::unique_ptr<Passenger>> rejected;
    
    if (!boat) return rejected;
    
    std::cout << "  Доступно жилетов: " << boat->getAvailableLifeJackets() << "\n";
    
    for (auto& p : candidates) {
        if (!tryAddPassenger(std::move(p), true)) {
            rejected.push_back(std::move(p));
        }
    }
    
    std::cout << "  Посажено: " << (candidates.size() - rejected.size()) 
              << ", отвергнуто: " << rejected.size() << "\n";
    
    return rejected;
}

std::unique_ptr<Vehicle> BoatBuilder::build() { 
    return std::move(boat); 
}