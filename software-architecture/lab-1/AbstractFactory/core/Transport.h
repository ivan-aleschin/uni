#pragma once
#include <vector>
#include <memory>
#include <string>
#include "../core/Driver.h"
#include "../core/Passenger.h"

class Transport {
protected:
    std::shared_ptr<Driver> driver;
    std::vector<Passenger> passengers;

public:
    virtual ~Transport() = default;

    virtual int get_places() const = 0;
    virtual bool add_passenger(const Passenger& passenger) = 0;
    
    // Дополнительные методы для контроля отправления
    virtual bool set_driver(std::shared_ptr<Driver> driver) = 0;
    virtual bool is_ready_to_go() const = 0;
    virtual std::string get_type() const = 0;
};
