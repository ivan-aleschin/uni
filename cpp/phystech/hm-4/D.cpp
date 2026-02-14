#include <vector>
#include <iostream>
#include <windows.h>
#include <string>

using namespace std;

enum class months {
    January  = 1,
    February  = 2,
    March = 3,
    April = 4,
    May = 5,
    June = 6,
    July = 7,
    August = 8,
    September = 9,
    October = 10,
    November = 11,
    December = 12
};

int main()
{
    SetConsoleOutputCP(CP_UTF8);
    int number{0};
    const int big{31}, small{30}, feb1{28}, feb2{29};

    cout << "Введите месяц(1-12): " << endl;
    cin >> number;
    if ((0 < number) && (number < 13)){
        cout << "Дней в месяце: ";
    }
    months ans = static_cast<months>(number);

    switch(ans){
        case months::January:
            cout << big << endl;
            break;
        case months::February:
            cout << feb1 << " или " << feb2 << endl;
            break;
        case months::March:
            cout << big << endl;
            break;
        case months::April:
            cout << small << endl;
            break;
        case months::May:
            cout << big << endl;
            break;
        case months::June:
            cout << small << endl;
            break;
        case months::July:
            cout  << big << endl;
            break;
        case months::August:
            cout << big << endl;
            break;
        case months::September:
            cout << small << endl;
            break;
        case months::October:
            cout << big << endl;
            break;
        case months::November:
            cout << small << endl;
            break;
        case months::December:
            cout << big << endl;
            break;
        default:
            cout << "Введено неправильное число!" << endl;
            break;
    }

    return 0;
}
