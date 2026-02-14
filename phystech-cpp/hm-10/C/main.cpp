#include <iostream>

template<class ...Args>
void func(Args... args) {
    auto lm = [&, args...] {
        return lm(args...);
    };
    lm();
}

template<typename Func,typename Args...>
void func(Func func,auto Agrs... args) {
    func(auto args...);
}

int main() {

    return 0;
}

