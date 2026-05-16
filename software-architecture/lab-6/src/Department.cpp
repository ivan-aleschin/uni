#include "Department.h"

#include <iostream>
#include <utility>

Department::Department(std::string name) : name_(std::move(name)) {}

void Department::onMissingSubmission(const std::string& teacher,
                                     const std::string& discipline,
                                     int week) {
    std::cout << "[Department:" << name_
              << "] получено оповещение: преподаватель " << teacher
              << " не разместил успеваемость по «" << discipline
              << "» на неделе " << week << "\n";
}
