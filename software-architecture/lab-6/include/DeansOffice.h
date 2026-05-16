#pragma once

#include "IObserver.h"

#include <set>
#include <string>
#include <vector>

class Department;
class Teacher;

// ConcreteObserver — деканат. Подписывается на преподавателей,
// получает уведомления о размещении успеваемости и в конце недели
// проверяет, кто не сдал, после чего оповещает кафедру.
class DeansOffice : public IObserver {
public:
    explicit DeansOffice(Department& department);

    // Подписаться на преподавателя как Observer.
    void watch(Teacher& teacher);

    // Отписаться от преподавателя (тот больше не отслеживается).
    void unwatch(Teacher& teacher);

    // Колбэк наблюдателя.
    void update(const SubmissionInfo& info) override;

    // В конце недели: сверить список подписанных преподавателей
    // с теми, кто прислал уведомление, и оповестить кафедру о пропустивших.
    void checkWeek(int week, const std::vector<Teacher*>& teachers);

private:
    Department& department_;
    // Ключ — пара (имя преподавателя, номер недели).
    std::set<std::pair<std::string, int>> received_;
};
