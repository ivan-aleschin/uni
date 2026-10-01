CXX      := g++
CXXFLAGS := -std=c++20 -Wall -Wextra -O2
TARGET   := lab1

.PHONY: all test clean

all: $(TARGET)

$(TARGET): main.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

test: $(TARGET)
	@bash ./run_tests.sh

clean:
	rm -f $(TARGET)
