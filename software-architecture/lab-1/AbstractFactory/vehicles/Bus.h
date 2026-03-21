#pragma once
#include "../core/Transport.h"

class Bus : public Transport {
private:
    const int capacity = 30;
public:
    int get_places() const override;
    bool add_passenger(const Passenger& passenger) override;
    bool set_driver(std::shared_ptr<Driver> newDriver) override;
    bool is_ready_to_go() const override;
    std::string get_type() const override;
};
