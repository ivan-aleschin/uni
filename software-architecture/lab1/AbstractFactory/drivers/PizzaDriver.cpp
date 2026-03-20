#include "PizzaDriver.h"

std::shared_ptr<PizzaDriver> PizzaDriver::getInstance() {
    static std::shared_ptr<PizzaDriver> instance = std::shared_ptr<PizzaDriver>(new PizzaDriver());
    return instance;
}

std::string PizzaDriver::getCategory() const {
    return "D";
}