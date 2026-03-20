#pragma once

#include <string>

class Driver {
private:
    std::string name;
    std::string licenseCategory;
    
public:
    Driver(const std::string& name, const std::string& category) 
        : name(name), licenseCategory(category) {}
    
    std::string getCategory() const { return licenseCategory; }
    std::string getName() const { return name; }
    
    bool canDrive(const std::string& vehicleType) const {
        if (vehicleType == "Bus") return licenseCategory == "D";
        if (vehicleType == "Taxi") return licenseCategory == "B";
        if (vehicleType == "InflatableBoat") return licenseCategory == "B" || licenseCategory == "D";
        return false;
    }
};