#pragma once
#include "../core/Driver.h"
#include <memory>

class PizzaDriver : public Driver {
private:
    PizzaDriver() = default;

public:
    static std::shared_ptr<PizzaDriver> getInstance();
    std::string getCategory() const override;
};