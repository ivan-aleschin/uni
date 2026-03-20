#pragma once

#include <memory>
#include <string>
#include <vector>
#include "Passenger.h"

class Vehicle;

class VehicleBuilder {
public:
    virtual ~VehicleBuilder() = default;
    virtual void reset() = 0;
    virtual void setDriver(const std::string& name, const std::string& category) = 0;
    virtual bool addPassenger(std::unique_ptr<Passenger> passenger) = 0;
    virtual std::unique_ptr<Vehicle> build() = 0;
    virtual std::vector<std::unique_ptr<Passenger>> 
        tryAddPassengers(std::vector<std::unique_ptr<Passenger>> candidates) = 0;
    virtual std::string getErrors() const = 0;
};