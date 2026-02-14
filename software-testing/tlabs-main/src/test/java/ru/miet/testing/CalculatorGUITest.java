package ru.miet.testing;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.mockito.Mockito.*;
import java.awt.event.ActionEvent;
import javax.swing.JButton;

public class CalculatorGUITest {

    private CalculatorGUI calculatorGUI;
    private ActionListenerMock plusListenerMock;
    private ActionListenerMock minusListenerMock;
    private ActionListenerMock multiplyListenerMock;
    private ActionListenerMock divideListenerMock;

    @BeforeEach
    public void setUp() {
        calculatorGUI = new CalculatorGUI();
        
        // Создаем mock-слушатели для каждой кнопки
        plusListenerMock = new ActionListenerMock();
        minusListenerMock = new ActionListenerMock();
        multiplyListenerMock = new ActionListenerMock();
        divideListenerMock = new ActionListenerMock();
        
        // Устанавливаем слушатели
        calculatorGUI.setPlusButtonListener(plusListenerMock);
        calculatorGUI.setMinusButtonListener(minusListenerMock);
        calculatorGUI.setMultiplyButtonListener(multiplyListenerMock);
        calculatorGUI.setDivideButtonListener(divideListenerMock);
    }

    @Test
    public void testPlusButtonClickCallsListener() {
        // Arrange
        JButton plusButton = calculatorGUI.getPlusButton();
        
        // Act: Симулируем клик по кнопке "+"
        plusButton.doClick();
        
        // Assert: Проверяем, что слушатель был вызван
        assert plusListenerMock.isCalled() : "Plus button listener should be called";
    }

    @Test
    public void testMinusButtonClickCallsListener() {
        // Arrange
        JButton minusButton = calculatorGUI.getMinusButton();
        
        // Act: Симулируем клик по кнопке "-"
        minusButton.doClick();
        
        // Assert: Проверяем, что слушатель был вызван
        assert minusListenerMock.isCalled() : "Minus button listener should be called";
    }

    @Test
    public void testMultiplyButtonClickCallsListener() {
        // Arrange
        JButton multiplyButton = calculatorGUI.getMultiplyButton();
        
        // Act: Симулируем клик по кнопке "*"
        multiplyButton.doClick();
        
        // Assert: Проверяем, что слушатель был вызван
        assert multiplyListenerMock.isCalled() : "Multiply button listener should be called";
    }

    @Test
    public void testDivideButtonClickCallsListener() {
        // Arrange
        JButton divideButton = calculatorGUI.getDivideButton();
        
        // Act: Симулируем клик по кнопке "/"
        divideButton.doClick();
        
        // Assert: Проверяем, что слушатель был вызван
        assert divideListenerMock.isCalled() : "Divide button listener should be called";
    }

    @Test
    public void testDisplayErrorShowsMessageAndClearsResult() {
        // Arrange
        String errorMessage = "Test error message";
        
        // Act
        calculatorGUI.displayError(errorMessage);
        
        // Assert: Проверяем, что сообщение об ошибке отображается
        assert errorMessage.equals(calculatorGUI.getErrorLabel().getText()) : 
            "Error message should be displayed";
        assert calculatorGUI.getResultField().getText().isEmpty() : 
            "Result field should be cleared when error is displayed";
    }

    @Test
    public void testPrintResultShowsResultAndClearsError() {
        // Arrange
        double result = 42.0;
        calculatorGUI.displayError("Some error"); // Сначала показываем ошибку
        
        // Act
        calculatorGUI.printResult(result);
        
        // Assert: Проверяем, что результат отображается, а ошибка очищается
        assert String.valueOf(result).equals(calculatorGUI.getResultField().getText()) : 
            "Result should be displayed";
        assert calculatorGUI.getErrorLabel().getText().isEmpty() : 
            "Error should be cleared when result is displayed";
    }

    // Вспомогательный класс для mock-слушателей
    private static class ActionListenerMock implements java.awt.event.ActionListener {
        private boolean called = false;
        
        @Override
        public void actionPerformed(ActionEvent e) {
            called = true;
        }
        
        public boolean isCalled() {
            return called;
        }
        
        public void reset() {
            called = false;
        }
    }
}