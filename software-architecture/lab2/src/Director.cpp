#include "../include/Director.h"
#include "../include/VehicleBuilder.h"

void Director::setBuilder(VehicleBuilder* newBuilder) {
    builder = newBuilder;
}

void Director::constructEmptyBus() {
    if (!builder) return;
    builder->reset();
    builder->setDriver("Иван Петров", "D");
}

void Director::constructBusWithPassengers() {
    if (!builder) return;
    builder->reset();
    builder->setDriver("Сергей Иванов", "D");
    builder->addPassenger("adult", false);
    builder->addPassenger("adult", false);
    builder->addPassenger("benefit", false);
    builder->addPassenger("child", false);
    builder->addPassenger("child", false);
}

void Director::constructEmptyTaxi() {
    if (!builder) return;
    builder->reset();
    builder->setDriver("Алексей Сидоров", "B");
}

void Director::constructTaxiWithFamily() {
    if (!builder) return;
    builder->reset();
    builder->setDriver("Михаил Кузнецов", "B");
    builder->addPassenger("adult", false);
    builder->addPassenger("adult", false);
    builder->addPassenger("child", true);
}

void Director::constructBoatWithTourists() {
    if (!builder) return;
    builder->reset();
    builder->setDriver("Петр Капитан", "B");
    builder->addPassenger("adult", false);
    builder->addPassenger("adult", false);
    builder->addPassenger("adult", false);
    builder->addPassenger("child", true);
    builder->addPassenger("child", true);
}