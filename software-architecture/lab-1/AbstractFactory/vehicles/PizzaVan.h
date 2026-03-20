#pragma once
#include <vector>
#include <memory>
#include "../core/PizzaBox.h"
#include "../core/Driver.h"

class PizzaVan {
private:
    std::shared_ptr<Driver> driver;
    std::vector<PizzaBox> boxes;
    size_t capacity;

public:
    explicit PizzaVan(size_t maxBoxes = 10);
    virtual ~PizzaVan() = default;

    bool setDriver(std::shared_ptr<Driver> d);
    bool addPizzaBox(const PizzaBox& box);

    size_t getBoxCount() const { return boxes.size(); }
    size_t getCapacity() const { return capacity; }
    bool isReadyToDeliver() const;

    std::string getType() const { return "PizzaVan"; }
};