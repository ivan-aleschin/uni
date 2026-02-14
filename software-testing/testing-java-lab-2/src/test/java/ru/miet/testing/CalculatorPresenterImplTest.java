package ru.miet.testing;

import org.junit.Before;
import org.junit.Test;
import static org.mockito.Mockito.*;

public class CalculatorPresenterImplTest {
    private CalculatorView view;
    private Calculator calculator;
    private CalculatorPresenter presenter;

    @Before
    public void setUp() {
        view = mock(CalculatorView.class);
        calculator = new SimpleCalculator();
        presenter = new CalculatorPresenterImpl(view, calculator);
    }

    @Test
    public void testPlusValid() {
        when(view.getFirstArgumentAsString()).thenReturn("2");
        when(view.getSecondArgumentAsString()).thenReturn("3");
        presenter.onPlusClicked();
        verify(view).printResult(5.0);
    }

    @Test
    public void testMinusInvalidInput() {
        when(view.getFirstArgumentAsString()).thenReturn("abc");
        when(view.getSecondArgumentAsString()).thenReturn("1");
        presenter.onMinusClicked();
        verify(view).displayError(contains("Некорректный ввод"));
    }

    @Test
    public void testDivideByZero() {
        when(view.getFirstArgumentAsString()).thenReturn("2");
        when(view.getSecondArgumentAsString()).thenReturn("0");
        presenter.onDivideClicked();
        verify(view).displayError(contains("Ошибка"));
    }
}