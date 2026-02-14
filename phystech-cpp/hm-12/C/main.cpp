#include <iostream>
#include <type_traits>

template<size_t N>
struct factorial {
    static constexpr  double value = N * factorial<N - 1>::value;
};
template<>
struct factorial<0> {
    static constexpr  double value = 1;
};

template<size_t N>
struct exp {
    static constexpr  double value = exp<N-1>::value + (1/factorial<N>::value);
};

template<>
struct exp<1> {
    static constexpr  double value = 1;
};



int main() {
    constexpr  double f5 = exp<5>::value;
    std::cout << f5 << std::endl;

    return 0;
}