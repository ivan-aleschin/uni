#include "Taxi.h"
#include <iostream>

int Taxi::get_places() const {
    return capacity;
}

bool Taxi::set_driver(std::shared_ptr<Driver> newDriver) {
    if (this->driver) {
        std::cerr << "Driver already assigned to taxi!\n";
        return false;
    }
    if (newDriver->getCategory() != "B") {
        std::cerr << "Invalid driver category for taxi!\n";
        return false;
    }
    this->driver = newDriver;
    return true;
}

bool Taxi::add_passenger(const Passenger& passenger) {
    if (passengers.size() >= static_cast<size_t>(capacity)) {
        return false;
    }
    passengers.push_back(passenger);
    return true;
}

bool Taxi::is_ready_to_go() const {
    return driver && !passengers.empty() && passengers.size() <= static_cast<size_t>(capacity);
}

std::string Taxi::get_type() const {
    return "Taxi";
}
