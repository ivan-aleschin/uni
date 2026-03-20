#include "Bus.h"

Bus::Bus() : Vehicle(30) {}

std::string Bus::getType() const {
    return "Bus";
}
