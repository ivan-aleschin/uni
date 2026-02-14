#include <vector>
#include <iostream>
#include <windows.h>

using namespace std;

void merge (int* first, int* middle, int* last){
    int n = last - first;
    int* deck = new int[n];

    int* left = first;
    int* right = middle;
    for (int* d = deck; d!=deck+n;++d){
        if (left == middle){ *d = *right++;}
        else if (right==last ){ *d=*left++;}
        else if (*left < *right){ *d = *left++;}
        else{ *d = *right++;}
    }

    int *d = deck;
    while (first != middle){ *first++ = *d++;}
    while (middle != last){ *middle++ = *d++;}

    delete[] deck;
}

void mergesort (int* first, int* last){
    int n = last - first;
    if (n <= 1) return;
    int* middle = first + n/2;

    mergesort (first, middle);
    mergesort (middle, last);
    merge (first, middle, last);
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    int n{0};
    cout << "Введите число элементов массива: " << endl;
    cin >> n;
    cout << "Введите элементы массива через пробел или Enter: " << endl;
    int a[n];
    for(int i = 0; i < n; i++){
        cin >> a[i];
    }
    int* first = a;
    int* last = a + n;

    mergesort (first, last);

    cout << "Отсортированный массив: " << endl;
    for(int i = 0; i < n; i++){
        cout << a[i] << " ";
    }

    return 0;
}