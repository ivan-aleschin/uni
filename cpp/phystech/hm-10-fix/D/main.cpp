#include <iostream>

template<class Taken>
class Base {
public:
    void print() {
        self()->printImpl();
    }

    Taken* self() {
        return static_cast<Taken*> (this);
    }
};

class Taken : public Base<Taken> {
public:
    void printImpl() {
        std::cout << "Print from Taken" << std::endl;
    }
};

int main() {
    Taken input;
    input.print();

    return 0;
}