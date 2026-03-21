#pragma once
#include "TransportFactory.h"

class BusFactory : public TransportFactory {
public:
    std::shared_ptr<Transport> get_vehicle() override;
    std::shared_ptr<Driver> get_driver() override;
};
