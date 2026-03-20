#pragma once

#include "Component.h"
#include <vector>
#include <string>

class Section : public Component {
protected:
    std::vector<Component*> components;
    std::string sectionName;
public:
    Section(const std::string& name);
    virtual ~Section();
    void add(Component* c) override;
    int getBaggageWeight() const override;
    bool removePassenger(const std::string& name) override;
    void printLoadingMap() const;
};
