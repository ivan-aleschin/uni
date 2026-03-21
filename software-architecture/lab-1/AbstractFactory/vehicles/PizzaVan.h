#pragma once
#include <vector>
#include <memory>
#include <string>
#include "../core/Driver.h"
#include "../core/PizzaBox.h"

class PizzaVan {
private:
    std::shared_ptr<Driver> driver;
    std::vector<PizzaBox> boxes;
    const int capacity = 10;

public:
    int get_places() const;
    bool add_box(const PizzaBox& box);
    bool set_driver(std::shared_ptr<Driver> newDriver);
    bool is_ready_to_deliver() const;
    std::string get_type() const;
};
