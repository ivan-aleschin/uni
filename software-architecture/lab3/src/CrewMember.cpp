#include "../include/CrewMember.h"

CrewMember::CrewMember(const std::string& n) : name(n) {}

std::string CrewMember::getName() const { return name; }

int CrewMember::getBaggageWeight() const { return 0; }

void CrewMember::add(Component*) {
}

bool CrewMember::removePassenger(const std::string&) { return false; }

Pilot::Pilot(const std::string& n) : CrewMember(n) {}

Stewardess::Stewardess(const std::string& n) : CrewMember(n) {}