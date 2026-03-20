#pragma once

#include <string>

class Passenger {
protected:
    std::string type;
    bool needsSafetyEquipment;
    
public:
    Passenger(const std::string& type, bool needsSafety = false) 
        : type(type), needsSafetyEquipment(needsSafety) {}
    virtual ~Passenger() = default;
    
    std::string getType() const { return type; }
    bool requiresSafetyEquipment() const { return needsSafetyEquipment; }
    void setNeedsSafetyEquipment(bool needs) { needsSafetyEquipment = needs; }
    virtual double getTicketPrice() const = 0;
};

class AdultPassenger : public Passenger {
public:
    AdultPassenger() : Passenger("Adult", false) {}
    double getTicketPrice() const override { return 50.0; }
};

class BenefitPassenger : public Passenger {
public:
    BenefitPassenger() : Passenger("Benefit", false) {}
    double getTicketPrice() const override { return 25.0; }
};

class ChildPassenger : public Passenger {
public:
    ChildPassenger(bool needsSeat = true) : Passenger("Child", needsSeat) {}
    double getTicketPrice() const override { return 30.0; }
};