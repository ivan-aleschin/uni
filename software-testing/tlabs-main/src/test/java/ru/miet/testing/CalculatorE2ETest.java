package ru.miet.testing;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.awt.event.ActionEvent;
import javax.swing.JTextField;

public class CalculatorE2ETest {

    private CalculatorGUI gui;
    private CalculatorPresenter presenter;

    @BeforeEach
    public void setUp() {
        gui = new CalculatorGUI();
        presenter = new CalculatorPresenterImpl(gui);
        
        // Устанавливаем связь как в реальном приложении
        gui.setPlusButtonListener(e -> presenter.onPlusClicked());
        gui.setMinusButtonListener(e -> presenter.onMinusClicked());
        gui.setMultiplyButtonListener(e -> presenter.onMultiplyClicked());
        gui.setDivideButtonListener(e -> presenter.onDivideClicked());
    }

    @Test
    public void e2eTest_UserCanAddTwoNumbers() {
        // Симулируем действия пользователя:
        // 1. Пользователь вводит первое число
        gui.getFirstNumberField().setText("7");
        // 2. Пользователь вводит второе число
        gui.getSecondNumberField().setText("2");
        // 3. Пользователь нажимает кнопку "+"
        gui.getPlusButton().doClick();
        
        // Проверяем, что система работает корректно:
        assertEquals("9.0", gui.getResultField().getText());
        assertTrue(gui.getErrorLabel().getText().isEmpty());
    }

    @Test
    public void e2eTest_UserCanMultiplyNumbers() {
        // Действия пользователя
        gui.getFirstNumberField().setText("4");
        gui.getSecondNumberField().setText("5");
        gui.getMultiplyButton().doClick();
        
        // Проверка результата
        assertEquals("20.0", gui.getResultField().getText());
        assertTrue(gui.getErrorLabel().getText().isEmpty());
    }

    @Test
    public void e2eTest_UserSeesErrorWhenDividingByZero() {
        // Действия пользователя
        gui.getFirstNumberField().setText("10");
        gui.getSecondNumberField().setText("0");
        gui.getDivideButton().doClick();
        
        // Проверка, что ошибка показана пользователю
        assertEquals("Division by zero", gui.getErrorLabel().getText());
        assertTrue(gui.getResultField().getText().isEmpty());
    }

    @Test
    public void e2eTest_UserSeesErrorForInvalidInput() {
        // Действия пользователя (ввод нечисловых значений)
        gui.getFirstNumberField().setText("hello");
        gui.getSecondNumberField().setText("world");
        gui.getPlusButton().doClick();
        
        // Проверка, что система сообщает об ошибке ввода
        assertEquals("Please enter valid numbers", gui.getErrorLabel().getText());
        assertTrue(gui.getResultField().getText().isEmpty());
    }

    @Test
    public void e2eTest_OperationsChain() {
        // Тестируем последовательность операций как реальный пользователь
        gui.getFirstNumberField().setText("10");
        gui.getSecondNumberField().setText("2");
        gui.getDivideButton().doClick();
        
        assertEquals("5.0", gui.getResultField().getText());
        
        // Продолжаем вычисления с результатом
        gui.getFirstNumberField().setText(gui.getResultField().getText());
        gui.getSecondNumberField().setText("3");
        gui.getMultiplyButton().doClick();
        
        assertEquals("15.0", gui.getResultField().getText());
    }
}