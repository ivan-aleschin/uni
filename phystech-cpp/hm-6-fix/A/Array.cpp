//
// Created by LSG on 19.10.2021.
//

#include "Array.h"

Array::Array(const std::vector<int>& v): length(v.size()), vector(v) {
    array = new int[length];
    for (auto i = 0U; i < length; ++i) {
        array[i] = vector[i];
    }
};
Array::Array(int* v, int length) : length(length), vector(length, 0) {
    array = new int[length];
    for (auto i = 0U; i < length; ++i) {
        array[i] = v[i];
        vector[i] = v[i];
    };
};
Array::Array(int n) :length(1), vector(1, n) {
    array = new int[1];
    array[0] = n;
};
Array::~Array() {
    if (length) {
        delete[] array;
    }
}
Array::Array(const Array& other):length(other.length) {
    vector = other.vector;
    array = new int[length];
    for (auto i = 0; i < length; ++i) {
        array[i] = other.array[i];
    }
}
Array::Array(Array&& other) :length(other.length) {
    array = other.array;
    vector = std::move(other.vector);
    other.length = 0;
    other.array = nullptr;
}
Array& Array::operator= (const Array& other) {
    if (this == &other) return *this;
    if (length) {
        delete[] array;
    }
    length = other.length;
    array = new int[length];
    for (auto i = 0U; i < length; ++i) {
        array[i] = other.array[i];
    }
    vector = other.vector;
    return *this;
}
Array& Array::operator= (Array&& other) {
    if (this == &other) return *this;
    if (length) {
        delete[] array;
    }
    length = other.length;
    array = other.array;
    vector = std::move(other.vector);
    other.length = 0;
    other.array = nullptr;
    return *this;
}

void Array::print_the_Array() {
    for (auto i = 0U; i < length; ++i) {
        std::cout << vector[i] << ' ';
    }
    std::cout << std::endl;
}

