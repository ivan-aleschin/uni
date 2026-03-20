#pragma once

#include "Component.h"
#include <vector>
#include <string>
#include <utility>

class Airplane : public Component {
private:
    std::vector<Component*> components;
    int maxBaggageLoad;
    std::vector<std::pair<std::string, int>> removedBaggages;
public:
    Airplane(int maxLoad = 4000);
    ~Airplane() override;
    void add(Component* c) override;
    int getBaggageWeight() const override;
    bool removePassenger(const std::string& name) override;
    void assembleCrewAndPassengers();
    void adjustBaggageLoad();
    void printLoadingMap() const;
};

