#pragma once

#include "Vehicle.h"

class InflatableBoat : public Vehicle {
public:
    InflatableBoat() : Vehicle(6) {} 
    
    std::string getType() const override { return "InflatableBoat"; }
};