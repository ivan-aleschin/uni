#include "PizzaFactory.h"
#include "../drivers/PizzaDriver.h"

std::shared_ptr<PizzaVan> ConcretePizzaFactory::get_vehicle() {
    return std::make_shared<PizzaVan>();
}

std::shared_ptr<Driver> ConcretePizzaFactory::get_driver() {
    return PizzaDriver::getInstance();
}
