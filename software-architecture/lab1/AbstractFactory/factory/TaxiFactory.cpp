#include "TaxiFactory.h"
#include "../vehicles/Taxi.h"
#include "../drivers/TaxiDriver.h"

std::shared_ptr<Vehicle> TaxiFactory::createVehicle(
    const std::vector<Passenger>& passengers,
    std::vector<Passenger>& outNotSeated)
{
    outNotSeated.clear();
    
    auto driver = createDriver();
    if (!driver) {
        outNotSeated = passengers;
        return nullptr;
    }

    auto taxi = std::make_shared<Taxi>();

    if (!taxi->setDriver(driver)) {
        outNotSeated = passengers;
        return nullptr;
    }


    for (const auto& p : passengers) {
        if (!taxi->addPassenger(p)) {
            outNotSeated.push_back(p);
        }
    }


    if (!outNotSeated.empty()) {
        return nullptr;
    }

    return taxi;
}

std::shared_ptr<Driver> TaxiFactory::createDriver() {
    return TaxiDriver::getInstance();
}