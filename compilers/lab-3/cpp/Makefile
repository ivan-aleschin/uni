# ЛР3 ТАЯК — недетерминированный МП-автомат.
# Запускать из папки cpp/:
# make        — собрать ./lab3
# make test   — прогнать общие тесты ../tests/run_tests.sh (обе версии, C++ и Python)
# make clean  — удалить бинарь

# Компилятор задаём жёстко: во flake переменная окружения CXX указывает на кросс-компилятор
# riscv32 (он нужен микропроцессорным лабам), а нам нужен обычный g++ под эту машину.
CXX      = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -O2

lab3: main.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

test: lab3
	bash ../tests/run_tests.sh

clean:
	rm -f lab3

.PHONY: test clean
