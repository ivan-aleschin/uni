#include "PizzaVan.h"

PizzaVan::PizzaVan(size_t maxBoxes) : capacity(maxBoxes) {}

bool PizzaVan::setDriver(std::shared_ptr<Driver> d) {
    if (!d || driver) return false;
    driver = d;
    return true;
}

bool PizzaVan::addPizzaBox(const PizzaBox& box) {
    if (boxes.size() >= capacity) return false;
    boxes.push_back(box);
    return true;
}

bool PizzaVan::isReadyToDeliver() const {
    return driver && !boxes.empty();
}