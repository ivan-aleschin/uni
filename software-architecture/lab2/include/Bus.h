#pragma once

#include "Vehicle.h"

class Bus : public Vehicle {
private:
    double adultPrice;
    double benefitPrice;
    double childPrice;
    
public:
    Bus() : Vehicle(30), adultPrice(50.0), benefitPrice(25.0), childPrice(30.0) {}
    
    std::string getType() const override { return "Bus"; }
    
    double calculateTotalFare() const {
        double total = 0.0;
        for (const auto& p : passengers) {
            total += p->getTicketPrice();
        }
        return total;
    }
};