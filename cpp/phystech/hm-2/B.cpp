#include <vector>
#include <iostream>
#include <windows.h>
using namespace std;

int main() {
    SetConsoleOutputCP(CP_UTF8);
    //setlocale(LC_ALL,"rus");
    //SetConsoleCP(1251);
    //SetConsoleOutputCP(1251);

    vector <double> arr;
    double tmp, key;
    int l, j;
    cout << "Введите длину массива: " << endl;
    cin >> l;
    cout << "Введите элементы массива через Enter или Пробел: " << endl;

    for (int i = 0; i < l; i++){ // Ввод массива
        cin >> tmp;
        arr.push_back(tmp);
    }

    for (int i = 1; i < l; i++){ //Сортировка массива
        key = arr[i];
        j = i - 1;
        while ((j >= 0) && (arr[j] > key)){
            arr[j + 1] = arr[j];
            j -= 1;
        }
        arr[j+1] = key;
    }

    cout << "Отсортированный массив: " << endl;
    for(auto const &element: arr){
        cout << element << " ";
    }

    return 0;
}