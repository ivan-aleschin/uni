# ЛР4 ТАЯК: синтаксический анализатор C-light.
#   make          — собрать ./lab4
#   make test     — tests.sh: все примеры из examples/ в обоих режимах, сверка числа ошибок;
#                   заодно перестраивает таблицы в results/
#   make results  — то же, что test
#   make clean    — удалить бинарь (results/ остаётся)
# Явно g++: во флэйке CXX указывает на кросс-компилятор RISC-V для лаб по МПС.
CXX      := g++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -O2

lab4: main.cpp lexer.hpp grammar.hpp parser.hpp
	$(CXX) $(CXXFLAGS) -o $@ main.cpp

test: lab4
	bash tests.sh

results: test

clean:
	rm -f lab4

.PHONY: test results clean
