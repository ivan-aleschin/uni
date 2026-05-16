#include "DeansOffice.h"
#include "Department.h"
#include "SubmissionInfo.h"
#include "Teacher.h"

#include <iostream>

DeansOffice::DeansOffice(Department& department) : department_(department) {}

void DeansOffice::watch(Teacher& teacher) {
    teacher.registerObserver(this);
}

void DeansOffice::update(const SubmissionInfo& info) {
    received_.emplace(info.teacher, info.week);
    std::cout << "[DeansOffice] получено уведомление: " << info.teacher
              << " (неделя " << info.week << ", группа " << info.group << ")\n";
}

void DeansOffice::checkWeek(int week, const std::vector<Teacher*>& teachers) {
    std::cout << "[DeansOffice] проверка по итогам недели " << week << "...\n";
    for (auto* teacher : teachers) {
        if (received_.count({teacher->name(), week}) == 0) {
            department_.onMissingSubmission(teacher->name(),
                                            teacher->discipline(),
                                            week);
        }
    }
}
