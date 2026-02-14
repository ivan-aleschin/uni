#include <iostream>
#include <type_traits>

template <typename T, typename U>
struct decay_equiv :
        std::is_same<typename std::decay<T>::type, U>::type
{};

int main() {
    std::cout << std::boolalpha;
    std::cout << decay_equiv<int, int>::value << '\n';
    std::cout << decay_equiv<int&, int>::value << '\n';
    std::cout << decay_equiv<int[2], int*>::value << '\n';

    return 0;
}