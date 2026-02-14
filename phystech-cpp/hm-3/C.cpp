#include <vector>
#include <iostream>
#include <windows.h>
#include <algorithm>

using namespace std;

int main() {
    SetConsoleOutputCP(CP_UTF8);
    int n{0}, choice{0};
    cout << "Введите число элементов массива: " << endl;
    cin >> n;
    cout << "Введите элементы массива через пробел или Enter: " << endl;
    vector<int> a(n);
    for(int i = 0; i < n; i++){
        cin >> a[i];
    }
    cout << "Выберите тип сортировки цифрой 1 или 2: \n" << "1) По возрастанию\n" << "2) По убыванию" << endl;
    cin >> choice;
    if(--choice){
        sort(a.begin(), a.end(),
             [](int x, int y){
                 return (x > y);
             });
    } else{
        sort(a.begin(), a.end(),
             [](int x, int y){
                 return (x < y);
             });
    }


    cout << "Отсортированный массив: " << endl;
    for(int i = 0; i < n; i++){
        cout << a[i] << " ";
    }

    return 0;
}