#include <iostream>

class Film {
protected:
    int averageCriticsRating;
    int averageAudienceRating;
public:
    virtual int final_score() {
        return averageCriticsRating;
    }
};

class dictatorialWebsite : public Film {
public:
    virtual int final_score() override {
        return averageCriticsRating;
        //сайт не даёт зрителям выражать своё мнение оценки ставят только критики (скорее всего проплаченные :) )
    };
};

class coolWebsite : public Film
{
public:
    virtual int final_score() override {
        return averageCriticsRating + averageAudienceRating;
        //сайт даёт зрителям ставить оценки,тем самым проплаченные оценки критиков видно издалека
    };
};

int main() {
    return 0;
}
