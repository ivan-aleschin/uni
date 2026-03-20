#include <iostream>
#include <string>

class Logger {
private:
    Logger() {
        std::cout << "Logger created.\n";
    }
    static Logger* instance;

public:
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    static Logger* getInstance() {
        if (!instance) {
            instance = new Logger();
        }
        return instance;
    }

    void log(const std::string& message) {
        std::cout << "[LOG]: " << message << std::endl;
    }
};

Logger* Logger::instance = nullptr;

int main() {
    Logger* logger1 = Logger::getInstance();
    Logger* logger2 = Logger::getInstance();

    logger1->log("Hello Singleton!");
    logger2->log("Another message.");

    if (logger1 == logger2) {
        std::cout << "Both are the same instance!" << std::endl;
    }

    return 0;
}
