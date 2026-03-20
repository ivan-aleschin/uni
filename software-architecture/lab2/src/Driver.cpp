#include "../include/Driver.h"

Driver::Driver(const std::string& name, const std::string& category)
    : name(name), licenseCategory(category) {}

std::string Driver::getCategory() const {
    return licenseCategory;
}

std::string Driver::getName() const {
    return name;
}

bool Driver::canDrive(const std::string& vehicleType) const {
    if (vehicleType == "Bus") {
        return licenseCategory == "D";
    } else if (vehicleType == "Taxi") {
        return licenseCategory == "B";
    }
    return false;
}