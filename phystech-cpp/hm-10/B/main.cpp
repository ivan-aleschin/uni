#include <iostream>

template <typename T, typename... Args>
T* func(Args... arg) {
    return new T(arg...);
}

int main() {
    std::cout << "Integer:" << std::endl;
    std::cout << *func<int>(46) << std::endl;
    std::cout << "Double:" << std::endl;
    std::cout << *func<double>(47.69) << std::endl;

    return 0;
}

