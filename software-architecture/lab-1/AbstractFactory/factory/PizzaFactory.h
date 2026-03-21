#pragma once
#include <memory>
#include "../vehicles/PizzaVan.h"
#include "../core/Driver.h"

// Параллельная фабрика для доставки пиццы
class PizzaFactory {
public:
    virtual ~PizzaFactory() = default;
    
    virtual std::shared_ptr<PizzaVan> get_vehicle() = 0;
    virtual std::shared_ptr<Driver> get_driver() = 0;
};

class ConcretePizzaFactory : public PizzaFactory {
public:
    std::shared_ptr<PizzaVan> get_vehicle() override;
    std::shared_ptr<Driver> get_driver() override;
};
