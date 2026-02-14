#include<iostream>
#include<chrono>
#include <windows.h>

class Stopwatch {
public:
    void start() {
        start1 = std::chrono::steady_clock::now();
    }
    void stop() {
        stop1 = std::chrono::steady_clock::now();
        elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(stop1 - start1 + elapsed);
    }
    void print() {
        std::cout << "Программа выполнялась " << elapsed.count() << " секунд" << std::endl;
    }
private:
    std::chrono::steady_clock::time_point start1{std::chrono::steady_clock::now()};
    std::chrono::steady_clock::time_point stop1{std::chrono::steady_clock::now()};
    std::chrono::duration<double> elapsed{0};

};

int test() {
    int c{0};
    for(int i=0; i<100000000; ++i) {
        c+=1;
    }
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    Stopwatch myWatch;

    myWatch.start();
    test(); //Время выполнения одного такого теста 0.15-0.17 секунд
    myWatch.stop();
    test(); // Тест, который выполняется во время паузы
    myWatch.start();
    test(); // Тест после паузы
    myWatch.stop();

    myWatch.print(); // В итоге получаем число в два раза больше, чем при выполнение одного теста, значит 3
    // тест(посередине) не считался; число таких пауз неограниченно

    return 0;
}