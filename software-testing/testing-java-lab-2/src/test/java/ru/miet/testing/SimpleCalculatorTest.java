package ru.miet.testing;

import org.junit.Test;
import static org.junit.Assert.*;

public class SimpleCalculatorTest {
    private final Calculator calculator = new SimpleCalculator();

    @Test
    public void testSum() {
        assertEquals(5.0, calculator.sum(2, 3), 1e-8);
    }

    @Test
    public void testSubtract() {
        assertEquals(-1.0, calculator.subtract(2, 3), 1e-8);
    }

    @Test
    public void testMultiply() {
        assertEquals(6.0, calculator.multiply(2, 3), 1e-8);
    }

    @Test(expected = ArithmeticException.class)
    public void testDivideByZero() {
        calculator.divide(1, 0);
    }

    @Test
    public void testDivide() {
        assertEquals(2.0, calculator.divide(6, 3), 1e-8);
    }
}