#include "../include/Passenger.h"
#include <iostream>

Passenger::Passenger(const std::string& n, int b)
    : name(n), baggage(b), originalBaggage(b) {}

std::string Passenger::getName() const { return name; }

int Passenger::getBaggageWeight() const { return baggage; }

void Passenger::offloadBaggage(int kg) {
    if (kg > 0) {
        if (kg > baggage) kg = baggage;
        baggage -= kg;
    }
}

void Passenger::add(Component*) {
}

bool Passenger::removePassenger(const std::string&) { return false; }

void Passenger::printPassengerInfo() const {
    std::cout << "    - " << name << ": " << baggage << " kg";
    if (baggage < originalBaggage) {
        std::cout << " (снято " << (originalBaggage - baggage) << " кг)";
    }
    std::cout << std::endl;
}