#include "BusDriver.h"

std::shared_ptr<BusDriver> BusDriver::getInstance() {
    static std::shared_ptr<BusDriver> instance(new BusDriver());
    return instance;
}

std::string BusDriver::getCategory() const {
    return "D";
}
