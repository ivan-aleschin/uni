# ЛР2 ТАЯК: конечные автоматы
# Явно g++: flake выставляет CXX под RISC-V кросс-компилятор (для microprocessor-systems)
CXX      := g++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -O2

SRC = main.cpp automaton.cpp
HDR = automaton.h

lab2: $(SRC) $(HDR)
	$(CXX) $(CXXFLAGS) -o $@ $(SRC)

# Автотесты из tests/ (строки из cases.tsv, детерминизация, ошибки, --dot)
test: lab2
	bash tests/run_tests.sh

clean:
	rm -f lab2

.PHONY: test clean
