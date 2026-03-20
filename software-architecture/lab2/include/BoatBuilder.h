#pragma once

#include "VehicleBuilder.h"
#include "InflatableBoat.h"
#include <vector>
#include <sstream>
#include <iostream>

class BoatBuilder : public VehicleBuilder {
private:
    std::unique_ptr<InflatableBoat> boat;
    int availableLifeJackets;
    std::ostringstream errorLog;
    
    bool validateDriver(const std::string& category) {
        if (category != "B" && category != "D") {
            errorLog << "Ошибка: Для лодки нужны права категории B или D\n";
            return false;
        }
        return true;
    }
    
    bool validatePassenger(Passenger* p) {
        if (!p) {
            errorLog << "Ошибка: Пустой указатель на пассажира\n";
            return false;
        }
        
        p->setNeedsSafetyEquipment(true);
        

        if (availableLifeJackets <= 0) {
            errorLog << "Ошибка: Нет спасательных жилетов\n";
            return false;
        }
        
        if (boat->getPassengerCount() >= 6) {
            errorLog << "Ошибка: Лодка переполнена\n";
            return false;
        }
        
        return true;
    }
    
public:
    BoatBuilder() : availableLifeJackets(6) { reset(); }
    
    void reset() override {
        boat = std::make_unique<InflatableBoat>();
        availableLifeJackets = 6;
        errorLog.str("");
        errorLog.clear();
    }
    
    void setDriver(const std::string& name, const std::string& category) override {
        if (!validateDriver(category)) return;
        
        auto driver = std::make_unique<Driver>(name, category);
        if (!boat->setDriver(std::move(driver))) {
            errorLog << "Ошибка: Не удалось установить капитана\n";
        }
    }
    
    bool addPassenger(std::unique_ptr<Passenger> passenger) override {
        if (!passenger) {
            errorLog << "Ошибка: Попытка добавить пустого пассажира\n";
            return false;
        }
        
        if (!validatePassenger(passenger.get())) return false;
        
        if (!boat->addPassenger(std::move(passenger))) {
            errorLog << "Ошибка: Не удалось посадить пассажира\n";
            return false;
        }
        
        availableLifeJackets--;  // Выдали жилет
        return true;
    }
    
    std::unique_ptr<Vehicle> build() override {
        if (!boat->hasDriver()) {
            errorLog << "Ошибка: Нет капитана\n";
            throw std::runtime_error(errorLog.str());
        }
        if (boat->getPassengerCount() == 0) {
            errorLog << "Ошибка: Нет пассажиров\n";
            throw std::runtime_error(errorLog.str());
        }
        

        if (availableLifeJackets + boat->getPassengerCount() != 6) {
            errorLog << "Ошибка: Несоответствие выдачи жилетов. "
                     << "Пассажиров: " << boat->getPassengerCount() 
                     << ", осталось жилетов: " << availableLifeJackets << "\n";
            throw std::runtime_error(errorLog.str());
        }
        
        return std::move(boat);
    }
    
    std::vector<std::unique_ptr<Passenger>> 
    tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) override {
        std::vector<std::unique_ptr<Passenger>> rejected;
        int initialPassengers = boat->getPassengerCount();
        
        for (auto& p : candidates) {
            if (!addPassenger(std::move(p))) {
                rejected.push_back(std::move(p));
            }
        }
        
        int added = boat->getPassengerCount() - initialPassengers;
        if (added > 0) {
            std::cout << "    Посажено: " << added << ", отвергнуто: " << rejected.size() << "\n";
        }
        
        return rejected;
    }
    
    std::string getErrors() const override {
        return errorLog.str();
    }
    
    int getAvailableLifeJackets() const { 
        return availableLifeJackets; 
    }
};