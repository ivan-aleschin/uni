#include <iostream>

template<class Function, class ... Args >
void callFunction( Function func, Args ... args) {
    func(args...);
}

int func(int x, int y) {
    std::cout << "Values of variables passed to the function:" << std::endl;
    std::cout << "x = " << x << "; y = " << y << std::endl;
}

int main() {
    int x{1}, y{0};

    callFunction(func, x, y);

    return 0;
}