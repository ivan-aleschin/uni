#include "../include/EconomyClass.h"
#include "../include/Passenger.h"

EconomyClass::EconomyClass() : Section("Economy Class") {}

void EconomyClass::offloadExcessBaggage(int& excess, std::vector<std::pair<std::string, int>>& removed) {
    if (excess <= 0) return;

    for (auto& comp : components) {
        Passenger* pass = dynamic_cast<Passenger*>(comp);
        if (pass && excess > 0) {
            int curr = pass->getBaggageWeight();
            if (curr > 0) {
                int removeThis = std::min(excess, curr);
                removed.emplace_back(pass->getName(), removeThis);
                pass->offloadBaggage(removeThis);
                excess -= removeThis;
                if (excess <= 0) return;
            }
        }
    }
}