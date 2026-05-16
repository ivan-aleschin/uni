#pragma once

class IObserver;
struct SubmissionInfo;

// Subject — интерфейс наблюдаемого объекта. Реализуется преподавателем.
class IObservable {
public:
    virtual ~IObservable() = default;
    virtual void registerObserver(IObserver* observer) = 0;
    virtual void removeObserver(IObserver* observer) = 0;
    virtual void notifyObservers(const SubmissionInfo& info) = 0;
};
