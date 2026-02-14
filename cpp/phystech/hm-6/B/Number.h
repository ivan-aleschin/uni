#ifndef CPPPROJECTS_NUMBER_H
#define CPPPROJECTS_NUMBER_H
#include <iostream>

class Number
{
private:
    int _num;
    int _denom;
public:
    Number(int num = 0, int denom = 0) : _num(num), _denom(denom) {}

    Number& operator++(); // версия префикс
    Number& operator--(); // версия префикс

    Number operator++(int); // версия постфикс
    Number operator--(int); // версия постфикс

    void setNum(int num) { _num = num; }
    void setDenom(int denom) { _denom = denom; }
    int getNum() { return _num; }
    int getDenom() { return _denom; }

    Number reduction() {
        int min{0};
        if (_num > _denom){
            min = _denom;
        } else{
            min = _num;
        }
        for(int i = 2; i <= min; i++){
            if((_num % i == 0) && (_denom % i == 0)){
                _num /= i;
                _denom /= i;
                --i;
            }
        }
    }

    friend Number operator+(const Number &num, const Number &denom);
    friend Number operator-(const Number &num, const Number &denom);
    friend Number operator*(const Number &num, const Number &denom);
    friend Number operator/(const Number &num, const Number &denom);
    friend Number operator<(const Number &num, const Number &denom);
    friend std::ostream& operator<< (std::ostream &out, const Number &n);
};


#endif
