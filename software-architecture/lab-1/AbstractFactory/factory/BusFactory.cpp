#include "BusFactory.h"
#include "../vehicles/Bus.h"
#include "../drivers/BusDriver.h"

std::shared_ptr<Transport> BusFactory::get_vehicle() {
    return std::make_shared<Bus>();
}

std::shared_ptr<Driver> BusFactory::get_driver() {
    return BusDriver::getInstance();
}
