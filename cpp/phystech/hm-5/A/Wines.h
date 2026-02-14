#ifndef CPPPROJECTS_WINES_H
#define CPPPROJECTS_WINES_H

#include <string>
#include <iostream>
using namespace std;

class Wines {
private:
    string name{""};
    string color{""};
    int degrees{0};
    string sweetness{""};
    double rating{0.0};
public:
    void setWines(string _name, string _color, int _degrees, string _swetness, double _rating);
    void print();
    void write();
    string getCastillo();
    ~Wines();
};

#endif //CPPPROJECTS_WINES_H