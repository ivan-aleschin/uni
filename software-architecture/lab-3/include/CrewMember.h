#pragma once
#include "Component.h"
#include <string>

class CrewMember : public Component {
protected:
    std::string name;
public:
    CrewMember(const std::string& n);
    std::string getName() const;
    int getBaggageWeight() const override;
    void add(Component*) override;
    bool removePassenger(const std::string&) override;
};

class Pilot : public CrewMember {
public:
    Pilot(const std::string& n);
};

class Stewardess : public CrewMember {
public:
    Stewardess(const std::string& n);
};

