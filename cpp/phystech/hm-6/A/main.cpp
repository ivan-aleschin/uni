#include <iostream>
#include "windows.h"
#include <vector>
#include <utility>

class DynArray {
private:
    int * _data;
    size_t _lenght;
    int _v;

public:
    DynArray(size_t size) :
            _lenght(size) {
        _data = new int[_lenght];
    }

    ~DynArray() {
        delete [] _data;
    }

    int& operator[] (size_t index) {
        return _data[index];
    }

    int operator[] (size_t index) const {
        return _data[index];
    }

    size_t getLenght() const { return _lenght; };


    void clear()  {_v = 0;}

    DynArray(int i = 0, int j = 0): _v(i) {}

    DynArray(DynArray&& move): _v(move._v) {}

    DynArray& operator= (const DynArray& copy)
    {
        if (&copy == this) return *this;
        clear();
        _v = copy._v;
        return *this;
    }

    int getValue() {return _v;}
};

std::ostream& operator<< (std::ostream & out, const DynArray& right) {
    out << "[ ";
    for(size_t i = 0; i < right.getLenght(); ++i) {
        out << right[i] << " ";
    }
    out << "]";

    return out;
}



int main() {
    SetConsoleOutputCP(CP_UTF8);

    int tmp{0}, sizeV{0};
    size_t sizeA{0};

    std::cout << "Введите количество элементов массива: " << std::endl;
    std::cin >> sizeA;
    DynArray array (sizeA);
    std::cout << "Введите элементы массива через Space или Enter: " << std::endl;
    for (size_t i = 0; i < sizeA; i++) {
        std::cin >> tmp;
        array[i] = tmp;
    }
    std::cout << array << std::endl;

    std::vector<DynArray> myVec;
    std::cout << "Введите количество элементов вектора: " << std::endl;
    std::cin >> sizeV;
    std::cout << "Введите элементы вектора через Space или Enter: " << std::endl;
    for (int i = 0; i < sizeV; i++){
        std::cin >> tmp;;
        myVec.push_back(std::move(tmp));
    }
    std::cout << "Введенный вектор: " << std::endl;
    std::cout << "{ ";
    for (auto &element: myVec){
        std::cout << element.getValue() << " ";
    }
    std::cout << "}";

    return 0;
}