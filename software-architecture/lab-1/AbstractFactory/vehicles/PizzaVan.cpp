#include "PizzaVan.h"
#include <iostream>

int PizzaVan::get_places() const {
    return capacity;
}

bool PizzaVan::set_driver(std::shared_ptr<Driver> newDriver) {
    if (this->driver) {
        std::cerr << "Driver already assigned to pizza van!\n";
        return false;
    }
    if (newDriver->getCategory() != "C") {
        std::cerr << "Invalid driver category for pizza van!\n";
        return false;
    }
    this->driver = newDriver;
    return true;
}

bool PizzaVan::add_box(const PizzaBox& box) {
    if (boxes.size() >= static_cast<size_t>(capacity)) {
        return false;
    }
    boxes.push_back(box);
    return true;
}

bool PizzaVan::is_ready_to_deliver() const {
    return driver && !boxes.empty() && boxes.size() <= static_cast<size_t>(capacity);
}

std::string PizzaVan::get_type() const {
    return "PizzaVan";
}
