#pragma once

#include "Expression.h"

#include <memory>
#include <vector>

// Шесть терминальных правил соответствуют шести типам ошибок
// из задания. Порядок их применения настраивается клиентом через
// CompositeRule и важен (см. README).

class TabRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

class QuotesRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

class DashRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

class PunctuationSpaceRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

class MultipleSpacesRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

class MultipleNewlinesRule : public Expression {
public:
    void interpret(Context& ctx) override;
};

// NonterminalExpression — последовательно применяет все вложенные правила
// к одному и тому же контексту.
class CompositeRule : public Expression {
public:
    void add(std::unique_ptr<Expression> rule);
    void interpret(Context& ctx) override;

private:
    std::vector<std::unique_ptr<Expression>> rules_;
};
