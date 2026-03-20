#pragma once
#include "Component.h"
#include <string>

class Passenger : public Component {
private:
    std::string name;
    int baggage;
    int originalBaggage;
public:
    Passenger(const std::string& n, int b);
    std::string getName() const;
    int getBaggageWeight() const override;
    void offloadBaggage(int kg);
    void add(Component*) override;
    bool removePassenger(const std::string& nm) override;
    void printPassengerInfo() const;
};
