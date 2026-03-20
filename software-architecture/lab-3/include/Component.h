#pragma once
#include <string>

class Component {
public:
    virtual int getBaggageWeight() const = 0;

    virtual void add(Component* component) = 0;

    virtual bool removePassenger(const std::string& /*name*/) {
        return false;
    }

    virtual ~Component() = default;
};