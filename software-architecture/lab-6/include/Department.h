#pragma once

#include <string>

// Кафедра — получатель оповещений от деканата о преподавателях,
// которые вовремя не разместили текущую успеваемость. Не является
// участником паттерна Observer (это адресат финального действия),
// присутствует потому что фигурирует в условии задачи.
class Department {
public:
    explicit Department(std::string name);

    void onMissingSubmission(const std::string& teacher,
                             const std::string& discipline,
                             int week);

    const std::string& name() const { return name_; }

private:
    std::string name_;
};
