#include "Rules.h"
#include "Context.h"

#include <regex>

// 4. Неправильное использование табуляторов: один или несколько подряд
// идущих табов в обычном тексте заменяются на одинарный пробел.
void TabRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex("\t+"), " ");
}

// 3. Использование "..." как кавычек заменяется на «...».
void QuotesRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex("\"([^\"]*)\""), "«$1»");
}

// 2. Дефис, окружённый пробелами, заменяется на длинное тире.
// Дефис внутри слов (например, "что-то") не трогается.
void DashRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex(" - "), " — ");
}

// 5. Лишний пробел после открывающей скобки, перед закрывающей,
// перед запятой и перед точкой.
void PunctuationSpaceRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex(R"(\(\s+)"), "(");
    ctx.text = std::regex_replace(ctx.text, std::regex(R"(\s+\))"), ")");
    ctx.text = std::regex_replace(ctx.text, std::regex(R"(\s+,)"), ",");
    ctx.text = std::regex_replace(ctx.text, std::regex(R"(\s+\.)"), ".");
}

// 1. Несколько подряд идущих пробелов заменяются на один.
void MultipleSpacesRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex(" {2,}"), " ");
}

// 6. Три и более переводов строки подряд сводятся к двум (одна пустая
// строка — стандарт между абзацами).
void MultipleNewlinesRule::interpret(Context& ctx) {
    ctx.text = std::regex_replace(ctx.text, std::regex("\n{3,}"), "\n\n");
}

// Порядок важен: табы → кавычки → тире → пунктуация → пробелы → переносы строк.
CompositeRule::CompositeRule() {
    add(std::make_unique<TabRule>());
    add(std::make_unique<QuotesRule>());
    add(std::make_unique<DashRule>());
    add(std::make_unique<PunctuationSpaceRule>());
    add(std::make_unique<MultipleSpacesRule>());
    add(std::make_unique<MultipleNewlinesRule>());
}

void CompositeRule::add(std::unique_ptr<Expression> rule) {
    rules_.push_back(std::move(rule));
}

void CompositeRule::interpret(Context& ctx) {
    for (auto& rule : rules_) {
        rule->interpret(ctx);
    }
}
