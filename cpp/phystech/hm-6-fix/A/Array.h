//
// Created by LSG on 19.10.2021.
//

#ifndef CPPPROJECTS_ARRAY_H
#define CPPPROJECTS_ARRAY_H
#include <iostream>
#include <vector>

class Array
{
private:
    int length;
    int* array;
    std::vector<int> vector;
public:
    Array() :length(0), array(nullptr), vector() {};
    Array(const std::vector<int>& v);
    Array(int* v, int length);
    Array(int n);
    Array(const Array& other);
    Array(Array&& other);
    ~Array();
    Array& operator= (const Array& other);
    Array& operator= (Array&& other);

    void print_the_Array();
};


#endif //CPPPROJECTS_ARRAY_H
