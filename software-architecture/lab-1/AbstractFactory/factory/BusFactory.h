#pragma once
#include "TransportFactory.h"

class BusFactory : public TransportFactory {
public:
    std::shared_ptr<Vehicle> createVehicle(
        const std::vector<Passenger>& passengers,
        std::vector<Passenger>& outNotSeated) override;

    static std::shared_ptr<Driver> createDriver();
};