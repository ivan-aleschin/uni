#pragma once

class Context;

// AbstractExpression — общий интерфейс правила грамматики корректора.
// И терминальные правила, и составное (нетерминальное) правило реализуют
// один и тот же метод interpret(Context&).
class Expression {
public:
    virtual ~Expression() = default;
    virtual void interpret(Context& ctx) = 0;
};
