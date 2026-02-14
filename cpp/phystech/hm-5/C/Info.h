#ifndef CPPPROJECTS_INFO_H
#define CPPPROJECTS_INFO_H

#include <string>
#include <iostream>

class Values
{
private:
    int m_intValue;
    double m_dValue;
public:
    Values(int intValue, double dValue);

    // Делаем класс Display другом класса Values
    class Key{
        friend class Display;
        Key();
    };

    void setFlags(Key){
        m_intValue;
        m_dValue;
    }
};

class Display
{
private:
    bool m_displayIntFirst;
public:
    Display(bool displayIntFirst) { m_displayIntFirst = displayIntFirst; }

    void displayItem(Values &value);
};

#endif //CPPPROJECTS_INFO_H
