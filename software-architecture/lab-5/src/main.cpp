#include "Context.h"
#include "Rules.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

namespace {

std::string readFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << "Не удалось открыть файл: " << path << "\n";
        return {};
    }
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

} // namespace

int main(int argc, char** argv) {
    std::string inputPath = "assets/input.txt";
    if (argc > 1) {
        inputPath = argv[1];
    }

    Context ctx{readFile(inputPath)};
    if (ctx.text.empty()) {
        return 1;
    }

    std::cout << "=== Исходный текст ===\n" << ctx.text;
    if (ctx.text.back() != '\n') {
        std::cout << '\n';
    }

    CompositeRule corrector;
    corrector.interpret(ctx);

    std::cout << "\n=== Откорректированный текст ===\n" << ctx.text;
    if (ctx.text.empty() || ctx.text.back() != '\n') {
        std::cout << '\n';
    }
    return 0;
}
