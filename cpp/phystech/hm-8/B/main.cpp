#include <iostream>

double calculate(int a, int b){
    if(b == 0){
        throw std::invalid_argument("division by zero");
    }

    return (a*1.0/b);
}

class Array{
private:
    int size;
    int *arr;
public:
    Array(int sz): size(sz){arr = new int[sz];}
    int& operator[](int index){
        if(index > size){
            throw std::range_error("array overflow");
        }

        return arr[index];
    };
};

int main() {
    int numerator, denominator;
    std::cout << "Enter numerator:" << std::endl;
    std::cin >> numerator;
    std::cout << "Enter denominator:" << std::endl;
    std::cin >> denominator;

    try{
        std::cout << calculate(numerator, denominator) << std::endl;
    } catch(std::invalid_argument& e){
        std::cout << e.what() << std::endl;
    }

    int size, index;
    std::cout << "Enter size of array: " << std::endl;
    std::cin >> size;
    Array arr(size);
    std::cout << "Enter the index to which you want to assign a value(1): " << std::endl;
    std::cin >> index;
    try {
        arr[index] = 1;
        std::cout << arr[index] << std::endl;
        std::cout << "Mission: possible" << std::endl;
    } catch (std::range_error& e){
        std::cout << e.what() << std::endl;
    }

    return 0;
}