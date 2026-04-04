#pragma once

#include "VehicleBuilder.h"
#include "Passenger.h"


class Director {
private:
    VehicleBuilder* builder;
    
public:
    void setBuilder(VehicleBuilder* newBuilder) { builder = newBuilder; }
    
    void constructBusWithPassengers() {
        builder->reset();
        builder->setDriver("Сергей Иванов", "D");
        builder->addPassenger(std::make_unique<AdultPassenger>());
        builder->addPassenger(std::make_unique<AdultPassenger>());
        builder->addPassenger(std::make_unique<BenefitPassenger>());
        builder->addPassenger(std::make_unique<ChildPassenger>(false));
        builder->addPassenger(std::make_unique<ChildPassenger>(false));
    }
    
    void constructTaxiWithFamily() {
        builder->reset();
        builder->setDriver("Михаил Кузнецов", "B");

        builder->addPassenger(std::make_unique<AdultPassenger>()); 
        builder->addPassenger(std::make_unique<AdultPassenger>()); 
        builder->addPassenger(std::make_unique<ChildPassenger>(true)); 
    }
    
    void constructTaxiWithoutChildSeat() {
        builder->reset();
        builder->setDriver("Олег Петров", "B");
        builder->addPassenger(std::make_unique<AdultPassenger>()); 
        builder->addPassenger(std::make_unique<ChildPassenger>(true));
    }
};