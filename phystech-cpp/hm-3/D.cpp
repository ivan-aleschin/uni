#include <string>
#include <vector>
#include <iostream>
#include <windows.h>
#include <algorithm>
#include <functional>

using namespace std;

int main() {
    SetConsoleOutputCP(CP_UTF8);
    const int n{3};
    double tmp1{0.0}, tmp2{0.0};
    cout << "Введите первое число " << endl;
    cin >> tmp1;
    cout << "Введите второе число " << endl;
    cin >> tmp2;
    auto f = [](double a, double b) {return (a + b);};
    auto g = [](double a, double b) {return (a - b);};
    auto h = [](double a, double b) {return (a * b);};

    std::vector<std::function<double(double a, double b)>> v;
    v.push_back(f);
    v.push_back(g);
    v.push_back(h);

    for(int i = 0; i < n; i++) {
        double result = v[i](tmp1, tmp2);
        switch (i) {
            case 0:
                cout << "Операция +: " << endl;
                break;
            case 1:
                cout << "Операция -: " << endl;
                break;
            case 2:
                cout << "Операция *: " << endl;
                break;
        }
        cout << result << endl;
    }

    return 0;
}