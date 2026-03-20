#pragma once
#include "../core/Vehicle.h"

class Bus : public Vehicle {
public:
    Bus();
    std::string getType() const override;
};
