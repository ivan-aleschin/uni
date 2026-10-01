# ЛР4 ТАЯК: синтаксический анализатор C-light, версия на C++.
#   make          — собрать ./lab4
#   make test     — ../tests.sh: все примеры из ../examples в обоих режимах для C++ и Python,
#                   сверка числа ошибок и побайтное сравнение вывода двух версий
#   make results  — перестроить таблицы в ../results (то же, что делает test)
#   make clean    — удалить бинарь
# Явно g++: во флэйке CXX указывает на кросс-компилятор RISC-V для лаб по МПС.
CXX      := g++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -O2

lab4: main.cpp lexer.hpp grammar.hpp parser.hpp
	$(CXX) $(CXXFLAGS) -o $@ main.cpp

test: lab4
	bash ../tests.sh

results: test

clean:
	rm -f lab4

.PHONY: test results clean
