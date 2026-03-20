#include <iostream>
#include <memory>
#include <queue>
#include <vector>
#include "Director.h"
#include "BusBuilder.h"
#include "TaxiBuilder.h"
#include "BoatBuilder.h"
#include "Bus.h"
#include "Taxi.h"
#include "InflatableBoat.h"

void printVehicleInfo(const std::unique_ptr<Vehicle>& v, const std::string& builderErrors = "") {
    if (!v) {
        std::cout << "  Транспорт не создан!\n";
        if (!builderErrors.empty()) {
            std::cout << "  Ошибки:\n" << builderErrors;
        }
        return;
    }
    
    std::cout << "  Тип: " << v->getType() << "\n";
    std::cout << "  Пассажиров: " << v->getPassengerCount() << "/";
    
    if (v->getType() == "Bus") std::cout << "30";
    else if (v->getType() == "Taxi") std::cout << "4";
    else if (v->getType() == "InflatableBoat") std::cout << "6";
    
    std::cout << "\n  Водитель: " << (v->hasDriver() ? "есть" : "нет");
    std::cout << "\n" << std::string(40, '-') << "\n";
}


std::vector<std::unique_ptr<Vehicle>> createVehiclesFromQueue(
    std::queue<std::unique_ptr<Passenger>>& passengerQueue,
    TaxiBuilder& builder,
    const std::string& driverName,
    const std::string& driverCategory)
{
    std::vector<std::unique_ptr<Vehicle>> vehicles;
    int vehicleNum = 1;
    bool hasMorePassengers = true;
    
    while (!passengerQueue.empty() && hasMorePassengers) {
        std::cout << "\n  Создание такси #" << vehicleNum++ << ":\n";
        builder.reset();
        builder.setChildSeat(true); 
        builder.setDriver(driverName, driverCategory);
        
        std::vector<std::unique_ptr<Passenger>> batch;

        int taken = 0;
        std::queue<std::unique_ptr<Passenger>> tempQueue;
        
        while (!passengerQueue.empty() && taken < 4) {
            auto p = std::move(passengerQueue.front());
            passengerQueue.pop();
            
            if (p->getType() == "Adult" || p->getType() == "Child") {
                batch.push_back(std::move(p));
                taken++;
            } else {

                tempQueue.push(std::move(p));
            }
        }
        

        while (!tempQueue.empty()) {
            passengerQueue.push(std::move(tempQueue.front()));
            tempQueue.pop();
        }
        
        if (batch.empty()) {
            std::cout << "  Нет подходящих пассажиров для такси\n";
            hasMorePassengers = false;
            continue;
        }
        
        std::cout << "  Попытка посадить " << batch.size() << " пассажиров\n";
        auto rejected = builder.tryAddPassengers(std::move(batch));
        
        for (auto& p : rejected) {
            passengerQueue.push(std::move(p));
        }
        
        try {
            auto vehicle = builder.build();
            if (vehicle && vehicle->getPassengerCount() > 0) {
                std::cout << "  ✓ Создано такси с " << vehicle->getPassengerCount() << " пассажирами\n";
                vehicles.push_back(std::move(vehicle));
            } else {
                std::cout << "  ✗ Такси пустое, прекращаем создание\n";
                hasMorePassengers = false;
            }
        } catch (const std::exception& e) {
            std::cout << "  ✗ Не удалось создать такси: " << e.what() << "\n";
            std::cout << "  Детали: " << builder.getErrors();
            hasMorePassengers = false;
        }
    }
    
    return vehicles;
}


std::vector<std::unique_ptr<Vehicle>> createVehiclesFromQueue(
    std::queue<std::unique_ptr<Passenger>>& passengerQueue,
    BoatBuilder& builder,
    const std::string& driverName,
    const std::string& driverCategory)
{
    std::vector<std::unique_ptr<Vehicle>> vehicles;
    int vehicleNum = 1;
    
    while (!passengerQueue.empty()) {
        std::cout << "\n  Создание лодки #" << vehicleNum++ << ":\n";
        builder.reset();
        builder.setDriver(driverName, driverCategory);
        
        std::vector<std::unique_ptr<Passenger>> batch;
        int capacity = 6;
        
        for (int i = 0; i < capacity && !passengerQueue.empty(); ++i) {
            batch.push_back(std::move(passengerQueue.front()));
            passengerQueue.pop();
        }
        
        std::cout << "  Попытка посадить " << batch.size() << " пассажиров\n";
        std::cout << "  Доступно жилетов: " << builder.getAvailableLifeJackets() << "\n";
        
        auto rejected = builder.tryAddPassengers(std::move(batch));
        
        for (auto& p : rejected) {
            passengerQueue.push(std::move(p));
        }
        
        try {
            auto vehicle = builder.build();
            if (vehicle && vehicle->getPassengerCount() > 0) {
                std::cout << "  ✓ Создана лодка с " << vehicle->getPassengerCount() << " пассажирами\n";
                vehicles.push_back(std::move(vehicle));
            } else {
                std::cout << "  ✗ Лодка пуста, прекращаем создание\n";
                break;
            }
        } catch (const std::exception& e) {
            std::cout << "  ✗ Не удалось создать лодку: " << e.what() << "\n";
            std::cout << "  Детали: " << builder.getErrors();
            break;
        }
        
        if (!passengerQueue.empty() && builder.getAvailableLifeJackets() == 0) {
            std::cout << "  Закончились жилеты, прекращаем создание лодок\n";
            break;
        }
    }
    
    return vehicles;
}

int main() {
    std::cout << "=== СИСТЕМА КОНТРОЛЯ ТРАНСПОРТА ===\n";
    std::cout << "=== БЕЗОПАСНОСТЬ В BUILDER'АХ ===\n\n";
    
    Director director;
    

    std::cout << "1. ТАКСИ - ДЕТСКОЕ КРЕСЛО:\n";
    
    std::cout << "\nСоздание такси с семьей (кресло есть):\n";
    TaxiBuilder taxiBuilder;
    taxiBuilder.setChildSeat(true);  
    director.setBuilder(&taxiBuilder);
    
    try {
        director.constructTaxiWithFamily();
        auto taxi = taxiBuilder.build();
        printVehicleInfo(taxi);
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка: " << e.what() << "\n";
        std::cout << "Детали: " << taxiBuilder.getErrors();
    }
    
    std::cout << "\nСоздание такси с ребенком БЕЗ кресла:\n";
    TaxiBuilder taxiBuilder2;
    taxiBuilder2.setChildSeat(false);  
    director.setBuilder(&taxiBuilder2);
    
    try {
        director.constructTaxiWithoutChildSeat();
        auto taxi2 = taxiBuilder2.build();
        printVehicleInfo(taxi2);
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка (ожидаемо): " << e.what() << "\n";
        std::cout << "  Детали: " << taxiBuilder2.getErrors();
    }
    

    std::cout << "\n2. НАДУВНАЯ ЛОДКА - СПАСАТЕЛЬНЫЕ ЖИЛЕТЫ:\n";
    
    BoatBuilder boatBuilder;
    director.setBuilder(&boatBuilder);
    
    std::cout << "\nСоздание лодки с туристами:\n";
    try {
        director.constructBoatWithTourists();
        auto boat = boatBuilder.build();
        printVehicleInfo(boat);
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка: " << e.what() << "\n";
        std::cout << "Детали: " << boatBuilder.getErrors();
    }
    

    std::cout << "\nПопытка создать лодку с перегрузом:\n";
    BoatBuilder boatBuilder2;
    boatBuilder2.setDriver("Петр Капитан", "B");
    
    for (int i = 0; i < 7; i++) {
        bool result = boatBuilder2.addPassenger(std::make_unique<AdultPassenger>());
        std::cout << "  Пассажир " << (i+1) << ": " << (result ? "✓ посажен" : "✗ не посажен") 
                  << " (жилетов осталось: " << boatBuilder2.getAvailableLifeJackets() << ")\n";
    }
    
    try {
        auto boat2 = boatBuilder2.build();
        printVehicleInfo(boat2);
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка при сборке: " << e.what() << "\n";
        std::cout << "  Детали: " << boatBuilder2.getErrors();
    }
    

    std::cout << "\n3. ОБРАБОТКА ОЧЕРЕДИ ПАССАЖИРОВ:\n";
    

    auto createTestQueue = []() {
        std::queue<std::unique_ptr<Passenger>> q;

        for (int i = 0; i < 4; ++i) {
            q.push(std::make_unique<ChildPassenger>(true));
        }

        for (int i = 0; i < 4; ++i) {
            q.push(std::make_unique<AdultPassenger>());
        }

        for (int i = 0; i < 4; ++i) {
            q.push(std::make_unique<BenefitPassenger>());
        }
        return q;
    };
    
    auto queue1 = createTestQueue();
    std::cout << "В очереди " << queue1.size() << " пассажиров:\n";
    std::cout << "  - 4 ребенка (нуждаются в креслах/жилетах)\n";
    std::cout << "  - 4 взрослых\n";
    std::cout << "  - 4 льготника (только для автобуса)\n";
    

    std::cout << "\n--- СОЗДАНИЕ ТАКСИ ИЗ ОЧЕРЕДИ ---\n";
    TaxiBuilder taxiBuilder3;
    auto taxis = createVehiclesFromQueue(queue1, taxiBuilder3, "Иван Водитель", "B");
    std::cout << "\nСоздано такси: " << taxis.size() << "\n";
    std::cout << "Осталось в очереди: " << queue1.size() << "\n";
    

    if (!queue1.empty()) {
        std::cout << "\n--- СОЗДАНИЕ ЛОДКИ ИЗ ОЧЕРЕДИ ---\n";
        BoatBuilder boatBuilder3;
        auto boats = createVehiclesFromQueue(queue1, boatBuilder3, "Петр Капитан", "B");
        std::cout << "\nСоздано лодок: " << boats.size() << "\n";
        std::cout << "Осталось в очереди: " << queue1.size() << "\n";
    }
    
    std::cout << "\n=== РАБОТА ЗАВЕРШЕНА ===\n";
    return 0;
}