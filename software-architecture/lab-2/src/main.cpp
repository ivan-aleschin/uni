#include <iostream>
#include <memory>
#include <queue>
#include <vector>
#include "Director.h"
#include "BusBuilder.h"
#include "TaxiBuilder.h"
#include "Bus.h"
#include "Taxi.h"

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
    
    if (v->getType() == "Bus") {
        std::cout << "30\n";
        std::cout << "  Стоимость билетов:\n";
        std::cout << "    Взрослый: 50 руб.\n";
        std::cout << "    Льготный: 25 руб.\n";
        std::cout << "    Ребёнок:  30 руб.";
    }
    else if (v->getType() == "Taxi") {
        std::cout << "4\n";
        std::cout << "  Стоимость билетов:\n";
        std::cout << "    Взрослый: 50 руб.\n";
        std::cout << "    Ребёнок:  30 руб.";
    }
    
    std::cout << "\n  Водитель: " << (v->hasDriver() ? "есть" : "нет");
    
    if (!builderErrors.empty()) {
        std::cout << "\n  Замечания при сборке:\n" << builderErrors;
    }
    
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
    BusBuilder& builder,
    const std::string& driverName,
    const std::string& driverCategory)
{
    std::vector<std::unique_ptr<Vehicle>> vehicles;
    int vehicleNum = 1;
    
    while (!passengerQueue.empty()) {
        std::cout << "\n  Создание автобуса #" << vehicleNum++ << ":\n";
        builder.reset();
        builder.setDriver(driverName, driverCategory);
        
        std::vector<std::unique_ptr<Passenger>> batch;
        int capacity = 30;
        
        for (int i = 0; i < capacity && !passengerQueue.empty(); ++i) {
            batch.push_back(std::move(passengerQueue.front()));
            passengerQueue.pop();
        }
        
        std::cout << "  Попытка посадить " << batch.size() << " пассажиров\n";
        
        auto rejected = builder.tryAddPassengers(std::move(batch));
        
        for (auto& p : rejected) {
            passengerQueue.push(std::move(p));
        }
        
        try {
            auto vehicle = builder.build();
            if (vehicle && vehicle->getPassengerCount() > 0) {
                std::cout << "  ✓ Создан автобус с " << vehicle->getPassengerCount() << " пассажирами\n";
                vehicles.push_back(std::move(vehicle));
            } else {
                std::cout << "  ✗ Автобус пуст, прекращаем создание\n";
                break;
            }
        } catch (const std::exception& e) {
            std::cout << "  ✗ Не удалось создать автобус: " << e.what() << "\n";
            std::cout << "  Детали: " << builder.getErrors();
            break;
        }
    }
    
    return vehicles;
}

int main() {
    std::cout << "=== СИСТЕМА КОНТРОЛЯ ТРАНСПОРТА ===\n";
    std::cout << "=== БЕЗОПАСНОСТЬ В BUILDER'АХ ===\n\n";
    
    Director director;
    
    std::cout << "1. ТАКСИ - ДЕТСКОЕ КРЕСЛО И ПРАВА:\n";
    
    std::cout << "\nСоздание такси с семьей (кресло есть, водитель кат. B):\n";
    TaxiBuilder taxiBuilder;
    taxiBuilder.setChildSeat(true);  
    director.setBuilder(&taxiBuilder);
    
    try {
        director.constructTaxiWithFamily();
        auto taxi = taxiBuilder.build();
        printVehicleInfo(taxi, taxiBuilder.getErrors());
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
        printVehicleInfo(taxi2, taxiBuilder2.getErrors());
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка (ожидаемо): " << e.what() << "\n";
        std::cout << "  Детали: " << taxiBuilder2.getErrors();
    }

    std::cout << "\n2. АВТОБУС - ВОДИТЕЛЬСКИЕ ПРАВА, ЛЬГОТНИКИ И ЛИМИТЫ:\n";
    
    std::cout << "\nПопытка назначить водителя с неверной категорией (B вместо D) в автобус:\n";
    BusBuilder busBuilder;
    busBuilder.setDriver("Алексей Водитель", "B"); // Wrong category for bus
    busBuilder.addPassenger(std::make_unique<AdultPassenger>());
    try {
        auto bus = busBuilder.build();
        printVehicleInfo(bus);
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка (ожидаемо): " << e.what() << "\n";
        std::cout << "Детали: " << busBuilder.getErrors();
    }
    
    std::cout << "\nСоздание автобуса с льготными пассажирами:\n";
    BusBuilder busBuilder2;
    busBuilder2.setDriver("Алексей Водитель", "D");
    busBuilder2.addPassenger(std::make_unique<BenefitPassenger>());
    busBuilder2.addPassenger(std::make_unique<AdultPassenger>());
    try {
        auto bus2 = busBuilder2.build();
        std::cout << "✓ Успешно!\n";
        printVehicleInfo(bus2, busBuilder2.getErrors());
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка: " << e.what() << "\n";
        std::cout << "Детали: " << busBuilder2.getErrors();
    }

    std::cout << "\nПопытка создать автобус с перегрузом (лимит 30):\n";
    BusBuilder busBuilder3;
    busBuilder3.setDriver("Алексей Водитель", "D");
    
    int successfullyAdded = 0;
    for (int i = 0; i < 35; i++) {
        bool result = busBuilder3.addPassenger(std::make_unique<AdultPassenger>());
        if (result) successfullyAdded++;
    }
    std::cout << "  Посажено пассажиров: " << successfullyAdded << " из 35\n";
    if (successfullyAdded == 30) {
        std::cout << "  ✓ Лимит автобуса работает корректно!\n";
    }
    
    try {
        auto bus3 = busBuilder3.build();
        printVehicleInfo(bus3, busBuilder3.getErrors());
    } catch (const std::exception& e) {
        std::cout << "✗ Ошибка при сборке: " << e.what() << "\n";
        std::cout << "  Детали: " << busBuilder3.getErrors();
    }
    
    std::cout << "\n3. ОБРАБОТКА ОЧЕРЕДИ ПАССАЖИРОВ:\n";
    
    auto createTestQueue = []() {
        std::queue<std::unique_ptr<Passenger>> q;

        for (int i = 0; i < 4; ++i) {
            q.push(std::make_unique<ChildPassenger>(true));
        }

        for (int i = 0; i < 15; ++i) {
            q.push(std::make_unique<AdultPassenger>());
        }

        for (int i = 0; i < 15; ++i) {
            q.push(std::make_unique<BenefitPassenger>());
        }
        return q;
    };
    
    auto queue1 = createTestQueue();
    std::cout << "В очереди " << queue1.size() << " пассажиров:\n";
    std::cout << "  - 4 ребенка\n";
    std::cout << "  - 15 взрослых\n";
    std::cout << "  - 15 льготников (только для автобуса)\n";
    
    std::cout << "\n--- СОЗДАНИЕ ТАКСИ ИЗ ОЧЕРЕДИ ---\n";
    TaxiBuilder taxiBuilder3;
    auto taxis = createVehiclesFromQueue(queue1, taxiBuilder3, "Иван Водитель", "B");
    std::cout << "\nСоздано такси: " << taxis.size() << "\n";
    std::cout << "Осталось в очереди: " << queue1.size() << " (льготники и, возможно, оставшиеся взрослые/дети)\n";
    
    if (!queue1.empty()) {
        std::cout << "\n--- СОЗДАНИЕ АВТОБУСОВ ИЗ ОЧЕРЕДИ ---\n";
        BusBuilder busBuilderQueue;
        auto buses = createVehiclesFromQueue(queue1, busBuilderQueue, "Петр Водитель", "D");
        std::cout << "\nСоздано автобусов: " << buses.size() << "\n";
        std::cout << "Осталось в очереди: " << queue1.size() << "\n";
    }
    
    std::cout << "\n=== РАБОТА ЗАВЕРШЕНА ===\n";
    return 0;
}