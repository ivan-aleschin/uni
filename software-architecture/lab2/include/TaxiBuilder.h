#pragma once

#include "VehicleBuilder.h"
#include "Taxi.h"
#include <vector>
#include <sstream>

class TaxiBuilder : public VehicleBuilder {
private:
    std::unique_ptr<Taxi> taxi;
    bool hasChildSeat;
    std::ostringstream errorLog;
    
    bool validateDriver(const std::string& category) {
        if (category != "B") {
            errorLog << "Ошибка: Водитель такси должен иметь категорию B\n";
            return false;
        }
        return true;
    }
    
    bool validatePassenger(const Passenger* p) {

        if (p->getType() != "Adult" && p->getType() != "Child") {
            errorLog << "Ошибка: В такси можно только взрослых и детей. Попытка посадить: " << p->getType() << "\n";
            return false;
        }
        

        if (p->getType() == "Child" && p->requiresSafetyEquipment() && !hasChildSeat) {
            errorLog << "Ошибка: Ребенку нужно детское кресло, но оно не установлено\n";
            return false;
        }
        

        if (taxi->getPassengerCount() >= 4) {
            errorLog << "Ошибка: Такси заполнено\n";
            return false;
        }
        
        return true;
    }
    
public:
    TaxiBuilder() : hasChildSeat(false) { reset(); }
    
    void setChildSeat(bool available) { hasChildSeat = available; }
    
    void reset() override {
        taxi = std::make_unique<Taxi>();
        hasChildSeat = false;
        errorLog.str("");
        errorLog.clear();
    }
    
    void setDriver(const std::string& name, const std::string& category) override {
        if (!validateDriver(category)) return;
        
        auto driver = std::make_unique<Driver>(name, category);
        if (!taxi->setDriver(std::move(driver))) {
            errorLog << "Ошибка: Не удалось установить водителя\n";
        }
    }
    
    bool addPassenger(std::unique_ptr<Passenger> passenger) override {
        if (!passenger) {
            errorLog << "Ошибка: Попытка добавить пустого пассажира\n";
            return false;
        }
        
        if (!validatePassenger(passenger.get())) return false;
        
        if (!taxi->addPassenger(std::move(passenger))) {
            errorLog << "Ошибка: Не удалось добавить пассажира\n";
            return false;
        }
        return true;
    }
    
    std::unique_ptr<Vehicle> build() override {
        if (!taxi->hasDriver()) {
            errorLog << "Ошибка: Нет водителя\n";
            throw std::runtime_error(errorLog.str());
        }
        if (taxi->getPassengerCount() == 0) {
            errorLog << "Ошибка: Нет пассажиров\n";
            throw std::runtime_error(errorLog.str());
        }
        return std::move(taxi);
    }
    
    std::vector<std::unique_ptr<Passenger>> 
    tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) override {
        std::vector<std::unique_ptr<Passenger>> rejected;
        for (auto& p : candidates) {
            if (!addPassenger(std::move(p))) {
                rejected.push_back(std::move(p));
            }
        }
        return rejected;
    }
    
    std::string getErrors() const override {
        return errorLog.str();
    }
};