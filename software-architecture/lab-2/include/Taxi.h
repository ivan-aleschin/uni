#pragma once

#include "Vehicle.h"

class Taxi : public Vehicle {
public:
    Taxi() : Vehicle(4) {} 
    
    std::string getType() const override { return "Taxi"; }
};