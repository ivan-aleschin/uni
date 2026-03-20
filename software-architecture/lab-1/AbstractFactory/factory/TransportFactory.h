#pragma once
#include <memory>
#include <vector>
#include "../core/Vehicle.h"
#include "../core/Driver.h"
#include "../core/Passenger.h"

class TransportFactory {
public:
    virtual ~TransportFactory() = default;
    virtual std::shared_ptr<Vehicle> createVehicle(
        const std::vector<Passenger>& passengers,
        std::vector<Passenger>& outNotSeated) = 0;
};