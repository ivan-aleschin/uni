#pragma once
#include <vector>
#include <memory>
#include "../core/Driver.h"
#include "../core/Passenger.h"

class Vehicle {
protected:
    std::shared_ptr<Driver> driver;
    std::vector<Passenger> passengers;
    size_t capacity;

public:
    explicit Vehicle(size_t capacity);
    virtual ~Vehicle() = default;

    bool setDriver(std::shared_ptr<Driver> driver);
    bool addPassenger(const Passenger& passenger);

    bool isReadyToGo() const;

    virtual std::string getType() const = 0;
};
