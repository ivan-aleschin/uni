#include "Info.h"

Values::Values(int intValue, double dValue) {
    m_intValue = intValue;
    m_dValue = dValue;
}

void Display::displayItem(Values &value)
{
    if (m_displayIntFirst)
        std::cout << value.m_intValue << " " << value.m_dValue << '\n';
    else // или сначала выводим double
        std::cout << value.m_dValue << " " << value.m_intValue << '\n';
}