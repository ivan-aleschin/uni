#include "PizzaFactory.h"
#include "../drivers/PizzaDriver.h"

std::shared_ptr<PizzaVan> PizzaFactory::createDelivery(
    const std::vector<PizzaBox>& boxes,
    std::vector<PizzaBox>& outNotDelivered)
{
    outNotDelivered.clear();

    auto driver = createDriver();
    if (!driver) {
        outNotDelivered = boxes;
        return nullptr;
    }

    auto van = std::make_shared<PizzaVan>(10);

    if (!van->setDriver(driver)) {
        outNotDelivered = boxes;
        return nullptr;
    }

    for (const auto& box : boxes) {
        if (!van->addPizzaBox(box)) {
            outNotDelivered.push_back(box);
        }
    }

    if (!outNotDelivered.empty()) {
        return nullptr;
    }

    return van;
}

std::shared_ptr<Driver> PizzaFactory::createDriver() {
    return PizzaDriver::getInstance();
}