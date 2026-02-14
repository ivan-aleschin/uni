#ifndef CPPPROJECTS_ENERGY_H
#define CPPPROJECTS_ENERGY_H

#include <string>
#include <iostream>
#include <math.h>
using namespace std;

class Energy {
private:
    const double const1{1.6 * pow(10, -19)};
    const double const2{1.0 * pow(10,-7)};
    double ans;
public:
    void setInput1(double ad);
    void setInput2(double ad);
    void setInput3(double ad);
    double getOutput1();
    double getOutput2();
    double getOutput3();
    ~Energy();
};

#endif //CPPPROJECTS_ENERGY_H
