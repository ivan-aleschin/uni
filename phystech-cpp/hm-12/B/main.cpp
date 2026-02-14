#include <iostream>
#include <type_traits>

template<unsigned N>
struct factorial {
    static const unsigned value = factorial<N - 2>::value + factorial<N - 1>::value;
};

template<>
struct factorial<1> {
    static const unsigned value = 1;
};

template<>
struct factorial<2> {
    static const unsigned value = 1;
};

int main() {
    const unsigned f5 = factorial<5>::value;
    std::cout << f5 << std::endl;

    return 0;
}