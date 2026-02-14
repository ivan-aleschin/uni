#include <iostream>
#include <windows.h>
#include "Info.h"

int main()
{
    SetConsoleOutputCP(CP_UTF8);

    Values value(7, 8.4);
    Display display(false);

    value.setFlags();
    display.displayItem(value);

    return 0;
}
