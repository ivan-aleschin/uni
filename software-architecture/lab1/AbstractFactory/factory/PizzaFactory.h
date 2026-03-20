#pragma once
#include <memory>
#include <vector>
#include "../core/PizzaBox.h"
#include "../core/Driver.h"
#include "../vehicles/PizzaVan.h"

class PizzaFactory {
public:
    static std::shared_ptr<PizzaVan> createDelivery(
        const std::vector<PizzaBox>& boxes,
        std::vector<PizzaBox>& outNotDelivered);

    static std::shared_ptr<Driver> createDriver();
};