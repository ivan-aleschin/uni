#include <vector>
#include <iostream>
#include <windows.h>
#include <string>

using namespace std;

struct Wines {
    string name{""};
    string color{""};
    int degrees{0};
    string sweetness{""};
    double rating{0.0};

    void print() {
        cout << "Name: " << name << endl;
        cout << "Color: " << color << endl;
        cout << "Degrees: " << degrees << " %" << endl;
        cout << "Sweetness: " << sweetness << endl;
        cout << "Rating: " << rating << "/100"<< endl;
        cout << "\n";
    }

    void write() {
        cout << "Напиши название вина: " << endl;
        getline(cin, name);
        cout << "Напишите цвет вина(Red, Rose, White): " << endl;
        cin >> color;
        cout << "Напишите крепкость: " << endl;
        cin >> degrees;
        cout << "Напишите сладкость вина(dry, semisweet, sweet): " << endl;
        cin >> sweetness;
        cout << "Напишите рейтинг вина(Роскачество): " << endl;
        cin >> rating;
        cout << "\n";
    }

    ~Wines(){
        cout << "Вино " << name << " удалено!" << endl;
    }
};
int main()
{
    SetConsoleOutputCP(CP_UTF8);


    Wines castillo = {"CASTILLO SANTA BARBARA RESERVA", "Red", 13, "Dry", 84.2};
    Wines taka = {"TAKA SAUVIGNON BLANC MARLBOROUGH", "White", 13, "Dry", 84.84};
    Wines sanprimo = {"SANPRIMO ROSATO PUGLIA", "Ping", 13, "Semi-sweet", 81.32};

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

    return 0;
}
