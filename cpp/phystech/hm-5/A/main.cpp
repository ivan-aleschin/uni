#include <vector>
#include <iostream>
#include <windows.h>
#include <string>
#include "Wines.h"

using namespace std;



int main()
{
    SetConsoleOutputCP(CP_UTF8);

    Wines castillo, taka, sanprimo;
    castillo.setWines("CASTILLO SANTA BARBARA RESERVA", "Red", 13, "Dry", 84.2);
    taka.setWines("TAKA SAUVIGNON BLANC MARLBOROUGH", "White", 13, "Dry", 84.84);
    sanprimo.setWines("SANPRIMO ROSATO PUGLIA", "Ping", 13, "Semi-sweet", 81.32);

    vector<string> names{"castillo", "taka", "sanprimo"};
    Wines ad;
    string tmp{""};
    int need{0};

    cout << "Введите первое слово названия вина для простоты выбора: " << endl;
    getline(cin, tmp);
    names.push_back(tmp);
    ad.write();

    cout << "Вина на выбор: " << endl;
    for(int i = 0;i < names.size(); i++) {
        cout << i + 1 << ") " << names[i] << " ";
    }

    cout << "\n\n";
    cout << "Выберите номер вина, о котором хотите узнать: " << endl;
    cin >> need;

    switch (need) {
        case 1:
            castillo.print();
            break;
        case 2:
            taka.print();
            break;
        case 3:
            sanprimo.print();
            break;
        case 4:
            ad.print();
            break;
    }

    cout << "Также хочу посоветовать вино: " << endl;
    cout << castillo.getCastillo() << endl;
    cout << "(Это была реализация вывода через геттер)" << "\n\n";

    return 0;
}