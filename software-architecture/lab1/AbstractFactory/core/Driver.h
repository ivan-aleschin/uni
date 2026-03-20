#pragma once
#include <string>

class Driver {
public:
    virtual ~Driver() = default;
    virtual std::string getCategory() const = 0;
};
