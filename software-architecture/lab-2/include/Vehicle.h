#pragma once

#include <vector>
#include <memory>
#include <string>
#include "Driver.h"
#include "Passenger.h"

class Vehicle {
protected:
    std::unique_ptr<Driver> driver;
    std::vector<std::unique_ptr<Passenger>> passengers;
    int maxCapacity;
    
public:
    Vehicle(int capacity) : maxCapacity(capacity) {}
    virtual ~Vehicle() = default;
    
    bool addPassenger(std::unique_ptr<Passenger> passenger) {
        if (static_cast<int>(passengers.size()) >= maxCapacity)
            return false;
        passengers.push_back(std::move(passenger));
        return true;
    }
    
    bool setDriver(std::unique_ptr<Driver> newDriver) {
        if (driver) return false;
        driver = std::move(newDriver);
        return true;
    }
    
    int getPassengerCount() const { return passengers.size(); }
    bool hasDriver() const { return driver != nullptr; }
    virtual std::string getType() const = 0;
};