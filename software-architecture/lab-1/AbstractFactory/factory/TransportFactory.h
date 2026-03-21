#pragma once
#include <memory>
#include "../core/Transport.h"
#include "../core/Driver.h"

// Абстрактная фабрика (AbstractFactory из паттерна)
class TransportFactory {
public:
    virtual ~TransportFactory() = default;
    
    // Создание семейства связанных объектов
    virtual std::shared_ptr<Transport> get_vehicle() = 0;
    virtual std::shared_ptr<Driver> get_driver() = 0;
};
