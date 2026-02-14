#include <iostream>

template<class Taken>
class Film {
public:
    int final_score() {
        self()->final_score_Impl();
    }

protected:
    int averageCriticsRating;
    int averageAudienceRating;
private:
    Taken* self() {
        return static_cast<Taken*>(this);
    }
};

class dictatorialWebsite : public Film<dictatorialWebsite> {
public:
    int final_score_Impl() {
        return averageCriticsRating;
        //сайт не даёт зрителям выражать своё мнение оценки ставят только критики (скорее всего проплаченные :) )
    };
};

class coolWebsite : public Film<coolWebsite> {
public:
    int final_score_Impl() {
        return averageCriticsRating + averageAudienceRating;
        //сайт даёт зрителям ставить оценки,тем самым проплаченные оценки критиков видно издалека
    };
};

int main() {
    return 0;
}
