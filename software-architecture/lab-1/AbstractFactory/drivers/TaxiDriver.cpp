#include "TaxiDriver.h"

std::shared_ptr<TaxiDriver> TaxiDriver::getInstance() {
    static std::shared_ptr<TaxiDriver> instance(new TaxiDriver());
    return instance;
}

std::string TaxiDriver::getCategory() const {
    return "B";
}
