#include "../include/Bus.h"
#include "../include/Driver.h"
#include "../include/Passenger.h"
#include <iostream>

Bus::Bus() : Vehicle(30), adultPrice(50.0), benefitPrice(25.0), childPrice(30.0) {}

std::string Bus::getType() const {
    return "Bus";
}

double Bus::calculateTotalFare() const {
    double total = 0.0;
    for (const auto& passenger : passengers) {
        total += passenger->getTicketPrice();
    }
    return total;
}

void Bus::setPrices(double adult, double benefit, double child) {
    adultPrice = adult;
    benefitPrice = benefit;
    childPrice = child;
}