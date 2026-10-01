# ЛР2 ТАЯК: конечные автоматы
# Явно g++: flake выставляет CXX под RISC-V кросс-компилятор (для microprocessor-systems)
CXX      := g++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -O2

SRC = main.cpp automaton.cpp
HDR = automaton.h

lab2: $(SRC) $(HDR)
	$(CXX) $(CXXFLAGS) -o $@ $(SRC)

# Автотесты из ../tests: обе версии (C++ и Python) и сверка их вывода.
# Только C++: bash ../tests/run_tests.sh cpp
test: lab2
	bash ../tests/run_tests.sh

clean:
	rm -f lab2

.PHONY: test clean
