package ru.miet.testing;

public class SimpleCalculator implements Calculator {
    @Override
    public double sum(double a, double b) {
        return a + b;
    }

    @Override
    public double subtract(double a, double b) {
        return a - b;
    }

    @Override
    public double multiply(double a, double b) {
        return a * b;
    }

    @Override
    public double divide(double a, double b) {
        if (Math.abs(b) < 1e-8) {
            throw new ArithmeticException("Divider is too close to zero");
        }
        return a / b;
    }
}