#include "Bus.h"
#include <iostream>

int Bus::get_places() const {
    return capacity;
}

bool Bus::set_driver(std::shared_ptr<Driver> newDriver) {
    if (this->driver) {
        std::cerr << "Driver already assigned to bus!\n";
        return false;
    }
    if (newDriver->getCategory() != "D") {
        std::cerr << "Invalid driver category for bus!\n";
        return false;
    }
    this->driver = newDriver;
    return true;
}

bool Bus::add_passenger(const Passenger& passenger) {
    if (passengers.size() >= static_cast<size_t>(capacity)) {
        return false;
    }
    passengers.push_back(passenger);
    return true;
}

bool Bus::is_ready_to_go() const {
    return driver && !passengers.empty() && passengers.size() <= static_cast<size_t>(capacity);
}

std::string Bus::get_type() const {
    return "Bus";
}
