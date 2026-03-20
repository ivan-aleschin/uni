#include "Taxi.h"

Taxi::Taxi() : Vehicle(4) {}

std::string Taxi::getType() const {
    return "Taxi";
}
