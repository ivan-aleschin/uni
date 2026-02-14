#include <iostream>

constexpr bool is_prime(int a) {
    for (int d = 2; d <= a / 2; ++d) {
        if (a % d == 0) {
            return false;
        }
    }
    return a > 1;
}

constexpr int n_prime(int n) {
    int k = 2;
    while (n > 1) {
        k++;
        if (is_prime(k)) {
            n = n - 1;
        }
    }
    return k;
}

int main() {
    constexpr int res = n_prime(5);
    std::cout << res << '\n';

    return 0;
}