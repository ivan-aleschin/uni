#include "TaxiFactory.h"
#include "../vehicles/Taxi.h"
#include "../drivers/TaxiDriver.h"

std::shared_ptr<Transport> TaxiFactory::get_vehicle() {
    return std::make_shared<Taxi>();
}

std::shared_ptr<Driver> TaxiFactory::get_driver() {
    return TaxiDriver::getInstance();
}
