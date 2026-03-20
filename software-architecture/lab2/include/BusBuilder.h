#pragma once

#include "VehicleBuilder.h"
#include "Bus.h"
#include <vector>
#include <sstream>

class BusBuilder : public VehicleBuilder {
private:
    std::unique_ptr<Bus> bus;
    std::ostringstream errorLog;
    
    bool validateDriver(const std::string& category) {
        if (category != "D") {
            errorLog << "Ошибка: Водитель автобуса должен иметь категорию D\n";
            return false;
        }
        return true;
    }
    
    bool validatePassenger(const Passenger* p) {
        if (bus->getPassengerCount() >= 30) {
            errorLog << "Ошибка: Автобус заполнен\n";
            return false;
        }
        return true;
    }
    
public:
    BusBuilder() { reset(); }
    
    void reset() override {
        bus = std::make_unique<Bus>();
        errorLog.str("");
        errorLog.clear();
    }
    
    void setDriver(const std::string& name, const std::string& category) override {
        if (!validateDriver(category)) return;
        
        auto driver = std::make_unique<Driver>(name, category);
        if (!bus->setDriver(std::move(driver))) {
            errorLog << "Ошибка: Не удалось установить водителя\n";
        }
    }
    
    bool addPassenger(std::unique_ptr<Passenger> passenger) override {
        if (!validatePassenger(passenger.get())) return false;
        
        if (!bus->addPassenger(std::move(passenger))) {
            errorLog << "Ошибка: Не удалось добавить пассажира\n";
            return false;
        }
        return true;
    }
    
    std::unique_ptr<Vehicle> build() override {
        if (!bus->hasDriver()) {
            errorLog << "Ошибка: Нет водителя\n";
            throw std::runtime_error(errorLog.str());
        }
        if (bus->getPassengerCount() == 0) {
            errorLog << "Ошибка: Нет пассажиров\n";
            throw std::runtime_error(errorLog.str());
        }
        return std::move(bus);
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