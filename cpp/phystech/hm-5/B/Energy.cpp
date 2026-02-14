#include "Energy.h"

void Energy::setInput1(double ad){
    ans = ad * const1;
}
void Energy::setInput2(double ad){
    ans = ad * const2;
}

void Energy::setInput3(double ad){
    ans = ad;
}

double Energy::getOutput1(){
    return (ans/const1);
}

double Energy::getOutput2(){
    return (ans/const2);
}

double Energy::getOutput3(){
    return (ans);
}

Energy::~Energy(){
    cout << "Вино " << ans << " удалено!" << endl;
}