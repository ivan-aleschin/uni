#include <iostream>
#include <vector>
#include <windows.h>

using namespace std;

int binSearch(double x,vector <double> arr,int n){
    int l, r, s;
    l = 0;
    r = n - 1;

    while ( l <= r){
        s = (l + r)/2;
        if (arr[s] < x ){
            l = s + 1;
        }
        else if(arr[s] > x ){
            r = s - 1;
        }
        else {
            return 1;
        }
    }
    return 0;
}

int main() {
    SetConsoleOutputCP(CP_UTF8);

    vector <double> arr;
    double x, a; //     x - искомое число, a - массив для поиска
    int n;
    cout << "Введите длину массива: " << endl;
    cin >> n;
    cout << "Введите элементы массива (раздельно): " << endl;

    for (int i = 0; i < n; i++){
        cin >> a;
        arr.push_back(a);
    }

    cout << "Введите искомый элемент: " << endl;
    cin >> x;

    if (binSearch(x, arr, n)){
        cout << "Число есть в массиве" << endl;
    } else{
        cout << "Такого числа нет в массиве" << endl;
    }
    return 0;
}