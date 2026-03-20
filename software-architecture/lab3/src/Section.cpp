#include "../include/Section.h"
#include "../include/Passenger.h"
#include <iostream>

Section::Section(const std::string& name) : sectionName(name) {}

Section::~Section() {
    for (auto& c : components) delete c;
}

void Section::add(Component* c) {
    if (c) components.push_back(c);
}

int Section::getBaggageWeight() const {
    int total = 0;
    for (const auto& c : components) total += c->getBaggageWeight();
    return total;
}

bool Section::removePassenger(const std::string& name) {
    for (auto it = components.begin(); it != components.end(); ++it) {
        Passenger* p = dynamic_cast<Passenger*>(*it);
        if (p && p->getName() == name) {
            delete *it;
            components.erase(it);
            return true;
        }
    }
    return false;
}

void Section::printLoadingMap() const {
    std::cout << sectionName << " (макс. пассажиров: ";
    if (sectionName == "First Class") std::cout << "10";
    else if (sectionName == "Business Class") std::cout << "20";
    else if (sectionName == "Economy Class") std::cout << "150";
    std::cout << "):" << std::endl;

    int count = 0;
    for (const auto& c : components) {
        Passenger* p = dynamic_cast<Passenger*>(c);
        if (p) {
            p->printPassengerInfo();
            count++;
        }
    }
    std::cout << "  Всего пассажиров: " << count << std::endl;
    std::cout << "  Общий багаж: " << getBaggageWeight() << " кг" << std::endl;

    if (sectionName == "First Class") std::cout << "  Бесплатно: без ограничения" << std::endl;
    else if (sectionName == "Business Class") std::cout << "  Бесплатно: 35 кг на человека" << std::endl;
    else if (sectionName == "Economy Class") std::cout << "  Бесплатно: 20 кг на человека" << std::endl;
}