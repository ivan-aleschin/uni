#include "Wines.h"

void Wines::setWines(string _name, string _color, int _degrees, string _swetness, double _rating){
    name = _name;
    color = _color;
    degrees = _degrees;
    sweetness = _swetness;
    rating = _rating;
}

string Wines::getCastillo(){
    return name;
}

void Wines::print() {
    std::cout << "Name: " << name << std::endl;
    cout << "Color: " << color << endl;
    cout << "Degrees: " << degrees << " %" << endl;
    cout << "Sweetness: " << sweetness << endl;
    cout << "Rating: " << rating << "/100"<< endl;
    cout << "\n";
}

void Wines::write() {
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

Wines::~Wines(){
    cout << "Вино " << name << " удалено!" << endl;
}