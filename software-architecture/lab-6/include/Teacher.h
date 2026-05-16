#pragma once

#include "IObservable.h"

#include <string>
#include <vector>

// ConcreteSubject — преподаватель. Раз в неделю размещает текущую
// успеваемость, при этом уведомляет всех подписавшихся наблюдателей
// (в нашей задаче — деканат).
class Teacher : public IObservable {
public:
    Teacher(std::string name, std::string discipline);

    void registerObserver(IObserver* observer) override;
    void removeObserver(IObserver* observer) override;
    void notifyObservers(const SubmissionInfo& info) override;

    void submitGrades(const std::string& group, int week);

    const std::string& name() const { return name_; }
    const std::string& discipline() const { return discipline_; }

private:
    std::string name_;
    std::string discipline_;
    std::vector<IObserver*> observers_;
};
