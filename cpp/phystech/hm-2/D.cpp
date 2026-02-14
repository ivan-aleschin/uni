#include <vector>
#include <iostream>
#include <windows.h>
#include <algorithm>
using namespace std;

int* input (int size){ // Функция ввода
    int *arr = new int[size];
    for (int i = 0; i < size; i++){
        cin >> arr[i];
    }
    return arr;
}

int** fill_dyn_matrix(int *arr1, int *arr2, int x, int y){
    int** matrix = new int*[x];
    for(int i = 0; i < x + 1; i++){ //Создание матрицы
        matrix[i] = new int[y];
        for(int j = 0; j < y + 1; j++){
            matrix[i][j] = 0;
        }
    }

    for (int i = 0; i < x; i++){ //Алгоритм создания матрицы
        for (int j = 0; j < y; j++){
            if (arr1[i] == arr2[j]){
                matrix[i+1][j+1] = matrix[i][j] + 1;
            } else{
                if (matrix[i+1][j] >= matrix[i][j+1]){
                    matrix[i+1][j+1] = matrix[i+1][j];
                } else{
                    matrix[i+1][j+1] = matrix[i][j+1];
                }
            }
        }
    }
    /*
    for (int i = 0; i < x + 1; i++){
        for (int j = 0; j < y + 1; j++) {
            cout << matrix[i][j] << " ";
        }
        cout << endl;
    }
    */
    return matrix;
}

vector<int> LCS_DYN(int *arr1, int *arr2, int x, int y){ //Нахождение подпоследовательности в матрице
    int** matrix = fill_dyn_matrix(arr1, arr2, x, y);
    vector<int> ans;
    x -= 1;
    y -= 1;
    while ((x >= 0) && (y >= 0)){
        if (arr1[x] == arr2[y]){
            ans.push_back(arr1[x]);
            x -= 1;
            y -= 1;
        } else if(matrix[x][y+1] > matrix[x+1][y]){
            x -= 1;
        } else{
            y -= 1;
        }
    }
    reverse(ans.begin(), ans.end());

    return ans;
}

int main()
{
    SetConsoleOutputCP(CP_UTF8);
    //setlocale(LC_ALL,"rus");
    //SetConsoleCP(1251);
    //SetConsoleOutputCP(1251);

    int x = 0, y = 0;
    cout << "Введите размер первого массива: " << endl;
    cin >> x; // Задаем размер массива
    cout << "Введите размер второго массива: " << endl;
    cin >> y;
    cout << "Введите элементы первого массива: " << endl;
    int* arr1 =  input(x); // Функция ввода
    cout << "Введите элементы второго массива: " << endl;
    int* arr2 =  input(y);

    vector<int> ans = LCS_DYN(arr1, arr2, x, y);

    cout << "Общая подпоследовательность: " << endl;
    for (auto const &element: ans) {
        cout << element << " ";
    }

    return 0;
}