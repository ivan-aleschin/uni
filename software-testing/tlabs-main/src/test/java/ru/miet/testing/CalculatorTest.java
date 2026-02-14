package ru.miet.testing;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    public void setUp() {
        calculator = new CalculatorImpl();
    }

    @Test
    public void testSumPositiveNumbers() {
        assertEquals(5.0, calculator.sum(2.0, 3.0), 1e-8);
    }

    @Test
    public void testSumNegativeNumbers() {
        assertEquals(-5.0, calculator.sum(-2.0, -3.0), 1e-8);
    }

    @Test
    public void testSumMixedNumbers() {
        assertEquals(0.0, calculator.sum(-2.0, 2.0), 1e-8);
    }

    @Test
    public void testSumWithZero() {
        assertEquals(5.0, calculator.sum(5.0, 0.0), 1e-8);
        assertEquals(5.0, calculator.sum(0.0, 5.0), 1e-8);
    }

    @Test
    public void testSubtractPositiveNumbers() {
        assertEquals(1.0, calculator.subtract(3.0, 2.0), 1e-8);
    }

    @Test
    public void testSubtractNegativeResult() {
        assertEquals(-1.0, calculator.subtract(2.0, 3.0), 1e-8);
    }

    @Test
    public void testSubtractSameNumbers() {
        assertEquals(0.0, calculator.subtract(5.0, 5.0), 1e-8);
    }

    @Test
    public void testSubtractNegativeNumbers() {
        assertEquals(1.0, calculator.subtract(-2.0, -3.0), 1e-8);
    }

    @Test
    public void testMultiplyPositiveNumbers() {
        assertEquals(6.0, calculator.multiply(2.0, 3.0), 1e-8);
    }

    @Test
    public void testMultiplyWithZero() {
        assertEquals(0.0, calculator.multiply(5.0, 0.0), 1e-8);
        assertEquals(0.0, calculator.multiply(0.0, 5.0), 1e-8);
    }

    @Test
    public void testMultiplyNegativeNumbers() {
        assertEquals(6.0, calculator.multiply(-2.0, -3.0), 1e-8);
    }

    @Test
    public void testMultiplyMixedSigns() {
        assertEquals(-6.0, calculator.multiply(2.0, -3.0), 1e-8);
        assertEquals(-6.0, calculator.multiply(-2.0, 3.0), 1e-8);
    }

    @Test
    public void testDividePositiveNumbers() {
        assertEquals(2.0, calculator.divide(6.0, 3.0), 1e-8);
    }

    @Test
    public void testDivideFractionalResult() {
        assertEquals(0.5, calculator.divide(1.0, 2.0), 1e-8);
    }

    @Test
    public void testDivideNegativeNumbers() {
        assertEquals(2.0, calculator.divide(-6.0, -3.0), 1e-8);
    }

    @Test
    public void testDivideMixedSigns() {
        assertEquals(-2.0, calculator.divide(6.0, -3.0), 1e-8);
        assertEquals(-2.0, calculator.divide(-6.0, 3.0), 1e-8);
    }

    @Test
    public void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(5.0, 0.0));
    }

    @Test
    public void testDivideByVerySmallNumberBelowThreshold() {
        // Числа меньше 10e-8 должны вызывать исключение
        assertThrows(ArithmeticException.class, () -> calculator.divide(5.0, 1e-9));
        assertThrows(ArithmeticException.class, () -> calculator.divide(5.0, -1e-9));
    }

    @Test
    public void testDivideBySmallNumberAboveThreshold() {
        // Числа больше или равные 10e-8 должны работать нормально
        assertDoesNotThrow(() -> {
            double result = calculator.divide(5.0, 1e-7);
            assertEquals(5e7, result, 1e-8);
        });
        
        assertDoesNotThrow(() -> {
            double result = calculator.divide(5.0, -1e-7);
            assertEquals(-5e7, result, 1e-8);
        });
    }

    @Test
    public void testDivideExactlyAtThreshold() {
        // Проверка на граничном значении 10e-8
        assertDoesNotThrow(() -> calculator.divide(5.0, 1e-8));
        assertDoesNotThrow(() -> calculator.divide(5.0, -1e-8));
    }

    @Test
    public void testDivideZeroByNonZero() {
        assertEquals(0.0, calculator.divide(0.0, 5.0), 1e-8);
    }
}