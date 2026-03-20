#include "../include/Taxi.h"
#include "../include/Passenger.h"
#include "../include/Driver.h"

Taxi::Taxi() : Vehicle(4, true), childSeatAvailable(false) {}

std::string Taxi::getType() const {
    return "Taxi";
}

bool Taxi::canDepart() const {
    if (!Vehicle::canDepart()) return false;
    if (hasChildren() && !childSeatAvailable) {
        // std::cout << "Для ребенка требуется детское кресло!\n";
        return false;
    }
    return true;
}

bool Taxi::addPassenger(std::unique_ptr<Passenger> passenger) {
    if (passengers.size() >= maxCapacity)
        return false;
    passengers.push_back(std::move(passenger));
    return true;
}

void Taxi::setChildSeat(bool available) {
    childSeatAvailable = available;
}

bool Taxi::hasChildSeat() const {
    return childSeatAvailable;
}