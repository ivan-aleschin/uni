#pragma once
#include "../core/Vehicle.h"

class Taxi : public Vehicle {
public:
    Taxi();
    std::string getType() const override;
};
