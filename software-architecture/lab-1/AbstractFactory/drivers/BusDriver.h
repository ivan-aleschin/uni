#pragma once
#include "../core/Driver.h"
#include <memory>

class BusDriver : public Driver {
private:
    BusDriver() = default;

public:
    static std::shared_ptr<BusDriver> getInstance();
    std::string getCategory() const override;
};
