#include <iostream>

template <typename ... Args>
auto sum(Args... arg) {
    return (... + sizeof(arg));
}

int main() {
    std::cout << "Using the convolution expression: " << std::endl;
    std::cout << sum(1, 2.2, 3, 43.6, 5) << std::endl;

    return 0;
}