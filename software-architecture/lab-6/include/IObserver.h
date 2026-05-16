#pragma once

struct SubmissionInfo;

// Observer — интерфейс наблюдателя. Реализуется деканатом.
class IObserver {
public:
    virtual ~IObserver() = default;
    virtual void update(const SubmissionInfo& info) = 0;
};
