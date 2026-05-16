#pragma once

#include <string>

// Аналог StockInfo из примера методички: данные, которые субъект
// (преподаватель) передаёт наблюдателю (деканату) при изменении состояния.
struct SubmissionInfo {
    std::string teacher;
    std::string discipline;
    std::string group;
    int week;
};
