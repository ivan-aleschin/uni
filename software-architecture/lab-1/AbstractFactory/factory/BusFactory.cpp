#include "BusFactory.h"
#include "../vehicles/Bus.h"
#include "../drivers/BusDriver.h"

std::shared_ptr<Vehicle> BusFactory::createVehicle(
    const std::vector<Passenger>& passengers,
    std::vector<Passenger>& outNotSeated)
{
    outNotSeated.clear();
    
    auto driver = createDriver();
    if (!driver) {
        outNotSeated = passengers;
        return nullptr;
    }

    auto bus = std::make_shared<Bus>();

    if (!bus->setDriver(driver)) {
        outNotSeated = passengers;
        return nullptr;
    }

    for (const auto& p : passengers) {
        if (!bus->addPassenger(p)) {
            outNotSeated.push_back(p);
        }
    }

    if (!outNotSeated.empty()) {
        return nullptr;
    }

    return bus;
}

std::shared_ptr<Driver> BusFactory::createDriver() {
    return BusDriver::getInstance();
}