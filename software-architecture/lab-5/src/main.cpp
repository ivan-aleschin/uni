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

    // Клиент собирает грамматику. Порядок правил важен:
    //   TabRule — первым, чтобы привести табы к пробелам;
    //   QuotesRule — до пунктуации, чтобы не повредить содержимое кавычек;
    //   DashRule — до правила множественных пробелов (требует ровно " - ");
    //   PunctuationSpaceRule — до MultipleSpacesRule, иначе у нас останутся
    //   одинарные «лишние» пробелы перед точкой/запятой;
    //   MultipleSpacesRule — после всего, что вводит лишние пробелы;
    //   MultipleNewlinesRule — последним, после возможной нормализации.
    CompositeRule corrector;
    corrector.add(std::make_unique<TabRule>());
    corrector.add(std::make_unique<QuotesRule>());
    corrector.add(std::make_unique<DashRule>());
    corrector.add(std::make_unique<PunctuationSpaceRule>());
    corrector.add(std::make_unique<MultipleSpacesRule>());
    corrector.add(std::make_unique<MultipleNewlinesRule>());

    corrector.interpret(ctx);

    std::cout << "\n=== Откорректированный текст ===\n" << ctx.text;
    if (ctx.text.empty() || ctx.text.back() != '\n') {
        std::cout << '\n';
    }
    return 0;
}
