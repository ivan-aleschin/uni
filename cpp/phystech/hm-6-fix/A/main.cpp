#include <iostream>
#include <vector>

#include "Array.h"

int main() {
    int length{0}, tmp{0}, n{0};
    std::cout << "Enter the number of elements in the vector: " << std::endl;
    std::cin >> n;
    std::vector<int> vector(n);
    std::cout << "Enter vector elements: " << std::endl;
    for (int i = 0; i < n; i++) {
        std::cin >> tmp;
        vector[i] = tmp;
    }

    std::cout << "Enter the number of elements in the array: " << std::endl;
    std::cin >> length;
    int* arr = new int[length];
    std::cout << "Enter array elements: " << std::endl;
    for (int i = 0; i < length; ++i) {
        std::cin >> tmp;
        arr[i] = tmp;
    }

    Array v(arr, length);
    Array v1(vector);
    Array v2;
    Array v3;

    std::cout << "Created arrays:" << std::endl;
    v.print_the_Array();
    v1.print_the_Array();
    v2 = v;

    std::cout << "Results of copying:" << std::endl;
    v.print_the_Array();
    v2.print_the_Array();
    v3 = std::move(v);

    std::cout << "Results of moving:" << std::endl;
    v.print_the_Array();
    v3.print_the_Array();

    return 0;
}