package ru.miet.testing;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class CalculatorPresenterTest {

    private CalculatorView mockView;
    private Calculator mockCalculator;
    private CalculatorPresenterImpl presenter;

    @BeforeEach
    public void setUp() {
        mockView = mock(CalculatorView.class);
        mockCalculator = mock(Calculator.class);
        
        // Создаем реальный презентер, но подменяем ему калькулятор через рефлексию
        presenter = new CalculatorPresenterImpl(mockView);
        
        // Используем рефлексию для подмены калькулятора в презентере
        try {
            java.lang.reflect.Field calculatorField = CalculatorPresenterImpl.class.getDeclaredField("calculator");
            calculatorField.setAccessible(true);
            calculatorField.set(presenter, mockCalculator);
        } catch (Exception e) {
            fail("Failed to inject mock calculator: " + e.getMessage());
        }
    }

    @Test
    public void testOnPlusClickedWithValidNumbers() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");
        when(mockCalculator.sum(5.0, 3.0)).thenReturn(8.0);

        presenter.onPlusClicked();

        verify(mockView).printResult(8.0);
        verify(mockView, never()).displayError(anyString());
    }

    @Test
    public void testOnMinusClickedWithValidNumbers() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");
        when(mockCalculator.subtract(5.0, 3.0)).thenReturn(2.0);

        presenter.onMinusClicked();

        verify(mockView).printResult(2.0);
        verify(mockView, never()).displayError(anyString());
    }

    @Test
    public void testOnMultiplyClickedWithValidNumbers() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");
        when(mockCalculator.multiply(5.0, 3.0)).thenReturn(15.0);

        presenter.onMultiplyClicked();

        verify(mockView).printResult(15.0);
        verify(mockView, never()).displayError(anyString());
    }

    @Test
    public void testOnDivideClickedWithValidNumbers() {
        when(mockView.getFirstArgumentAsString()).thenReturn("6");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");
        when(mockCalculator.divide(6.0, 3.0)).thenReturn(2.0);

        presenter.onDivideClicked();

        verify(mockView).printResult(2.0);
        verify(mockView, never()).displayError(anyString());
    }

    @Test
    public void testOnDivideClickedWithDivisionByZero() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("0");
        when(mockCalculator.divide(5.0, 0.0)).thenThrow(new ArithmeticException("Division by zero"));

        presenter.onDivideClicked();

        verify(mockView).displayError("Division by zero");
        verify(mockView, never()).printResult(anyDouble());
    }

    @Test
    public void testWithEmptyFirstArgument() {
        when(mockView.getFirstArgumentAsString()).thenReturn("");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");

        presenter.onPlusClicked();

        verify(mockView).displayError("Please enter both numbers");
        verify(mockView, never()).printResult(anyDouble());
    }

    @Test
    public void testWithEmptySecondArgument() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("");

        presenter.onPlusClicked();

        verify(mockView).displayError("Please enter both numbers");
        verify(mockView, never()).printResult(anyDouble());
    }

    @Test
    public void testWithInvalidNumbers() {
        when(mockView.getFirstArgumentAsString()).thenReturn("abc");
        when(mockView.getSecondArgumentAsString()).thenReturn("3");

        presenter.onPlusClicked();

        verify(mockView).displayError("Please enter valid numbers");
        verify(mockView, never()).printResult(anyDouble());
    }

    @Test
    public void testWithVerySmallDivisor() {
        when(mockView.getFirstArgumentAsString()).thenReturn("5");
        when(mockView.getSecondArgumentAsString()).thenReturn("0.000000001"); // 1e-9
        when(mockCalculator.divide(5.0, 1e-9)).thenThrow(new ArithmeticException("Division by zero"));

        presenter.onDivideClicked();

        verify(mockView).displayError("Division by zero");
        verify(mockView, never()).printResult(anyDouble());
    }
}