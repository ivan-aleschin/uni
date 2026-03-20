#pragma once
#include "../core/Driver.h"
#include <memory>

class TaxiDriver : public Driver {
private:
    TaxiDriver() = default;

public:
    static std::shared_ptr<TaxiDriver> getInstance();
    std::string getCategory() const override;
};
