#include "Teacher.h"
#include "IObserver.h"
#include "SubmissionInfo.h"

#include <algorithm>
#include <iostream>
#include <utility>

Teacher::Teacher(std::string name, std::string discipline)
    : name_(std::move(name)), discipline_(std::move(discipline)) {}

void Teacher::registerObserver(IObserver* observer) {
    observers_.push_back(observer);
}

void Teacher::removeObserver(IObserver* observer) {
    observers_.erase(std::remove(observers_.begin(), observers_.end(), observer),
                     observers_.end());
}

void Teacher::notifyObservers(const SubmissionInfo& info) {
    for (auto* observer : observers_) {
        observer->update(info);
    }
}

void Teacher::submitGrades(const std::string& group, int week) {
    std::cout << "[Teacher] " << name_ << " разместил успеваемость по «"
              << discipline_ << "» для группы " << group
              << " на неделе " << week << "\n";
    SubmissionInfo info{name_, discipline_, group, week};
    notifyObservers(info);
}
