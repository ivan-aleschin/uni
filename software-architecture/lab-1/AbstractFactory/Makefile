CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Icore -Ivehicles -Idrivers -Ifactory -Iutils

TARGET = transport_factory

SRCS = \
    main.cpp \
    core/Vehicle.cpp \
    vehicles/Taxi.cpp \
    vehicles/Bus.cpp \
    vehicles/PizzaVan.cpp \
    drivers/TaxiDriver.cpp \
    drivers/BusDriver.cpp \
    drivers/PizzaDriver.cpp \
    factory/TaxiFactory.cpp \
    factory/BusFactory.cpp \
    factory/PizzaFactory.cpp \
    utils/Simulation.cpp

OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(OBJS) -o $(TARGET)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run
