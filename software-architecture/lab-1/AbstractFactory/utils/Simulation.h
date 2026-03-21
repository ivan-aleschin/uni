#pragma once
#include "../factory/TransportFactory.h"
#include "../factory/PizzaFactory.h"
#include <queue>
#include "../core/Passenger.h"
#include "../core/PizzaBox.h"

class Simulation {
public:
    // Клиент взаимодействует только с абстрактной фабрикой (TransportFactory)
    // Он не знает, такси это или автобус, и не знает их вместимость.
    static void dispatchPassengers(TransportFactory& factory, std::queue<Passenger>& passengers);
    
    // Аналогично для пиццы
    static void dispatchPizza(PizzaFactory& factory, std::queue<PizzaBox>& boxes);

    static void runAll();
};
