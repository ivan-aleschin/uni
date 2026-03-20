#include "Vehicle.h"

Vehicle::Vehicle(size_t capacity) : capacity(capacity) {}

bool Vehicle::setDriver(std::shared_ptr<Driver> d) {
    if (driver) return false;
    driver = d;
    return true;
}

bool Vehicle::addPassenger(const Passenger& p) {
    if (passengers.size() >= capacity) return false;
    passengers.push_back(p);
    return true;
}

bool Vehicle::isReadyToGo() const {
    return driver && !passengers.empty();
}
