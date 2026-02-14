#include <iostream>
#include <type_traits>

template<unsigned N>
struct factorial {
    static const unsigned value = N * factorial<N - 1>::value;
};
template<>
struct factorial<0> {
    static const unsigned value = 1;
};



template<size_t N, size_t K>
struct C {
    static const size_t T = N - K;
    static const size_t value = factorial<N-1>::value / factorial<K>::value / factorial<T>::value + factorial<N-1>::value / factorial<K-1>::value / factorial<T-1>::value;
};
template<>
struct C<0, 0> {
    static const size_t value = 1;
};

int main() {
    const size_t i = C<5, 2>::value;
    std::cout << i << std::endl;

    return 0;
}