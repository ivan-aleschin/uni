package ru.miet.testing;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorIntegrationTest {

    private CalculatorView view;
    private Calculator calculator;
    private CalculatorPresenter presenter;

    @BeforeEach
    public void setUp() {
        // Создаем реальные компоненты (не моки!)
        view = new CalculatorGUI();
        calculator = new CalculatorImpl();
        
        // Для интеграционного тестирования нам нужно создать презентер с реальным калькулятором
        // Но поскольку CalculatorPresenterImpl создает калькулятор внутри, нам нужно:
        presenter = new CalculatorPresenterImpl(view);
        
        // Устанавливаем связь между GUI и презентером
        ((CalculatorGUI) view).setPlusButtonListener(e -> presenter.onPlusClicked());
        ((CalculatorGUI) view).setMinusButtonListener(e -> presenter.onMinusClicked());
        ((CalculatorGUI) view).setMultiplyButtonListener(e -> presenter.onMultiplyClicked());
        ((CalculatorGUI) view).setDivideButtonListener(e -> presenter.onDivideClicked());
    }

    @Test
    public void testFullIntegration_ValidAddition() {
        // Arrange: Устанавливаем значения в поля ввода
        ((CalculatorGUI) view).getFirstNumberField().setText("5");
        ((CalculatorGUI) view).getSecondNumberField().setText("3");
        
        // Act: Вызываем операцию сложения
        presenter.onPlusClicked();
        
        // Assert: Проверяем, что результат отобразился правильно
        assertEquals("8.0", ((CalculatorGUI) view).getResultField().getText());
        assertTrue(((CalculatorGUI) view).getErrorLabel().getText().isEmpty());
    }

    @Test
    public void testFullIntegration_DivisionByZero_ShowsError() {
        // Arrange
        ((CalculatorGUI) view).getFirstNumberField().setText("10");
        ((CalculatorGUI) view).getSecondNumberField().setText("0");
        
        // Act
        presenter.onDivideClicked();
        
        // Assert
        assertEquals("Division by zero", ((CalculatorGUI) view).getErrorLabel().getText());
        assertTrue(((CalculatorGUI) view).getResultField().getText().isEmpty());
    }

    @Test
    public void testFullIntegration_InvalidInput_ShowsError() {
        // Arrange
        ((CalculatorGUI) view).getFirstNumberField().setText("abc");
        ((CalculatorGUI) view).getSecondNumberField().setText("3");
        
        // Act
        presenter.onPlusClicked();
        
        // Assert
        assertEquals("Please enter valid numbers", ((CalculatorGUI) view).getErrorLabel().getText());
        assertTrue(((CalculatorGUI) view).getResultField().getText().isEmpty());
    }

    @Test
    public void testFullIntegration_EmptyFields_ShowsError() {
        // Arrange
        ((CalculatorGUI) view).getFirstNumberField().setText("");
        ((CalculatorGUI) view).getSecondNumberField().setText("3");
        
        // Act
        presenter.onPlusClicked();
        
        // Assert
        assertEquals("Please enter both numbers", ((CalculatorGUI) view).getErrorLabel().getText());
        assertTrue(((CalculatorGUI) view).getResultField().getText().isEmpty());
    }
}