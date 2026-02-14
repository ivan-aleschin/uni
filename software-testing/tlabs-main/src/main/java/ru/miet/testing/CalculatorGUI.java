package ru.miet.testing;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionListener;

public class CalculatorGUI implements CalculatorView {
    private JFrame frame;
    private JTextField firstNumberField;
    private JTextField secondNumberField;
    private JTextField resultField;
    private JLabel errorLabel;
    
    // Явное хранение ссылок на кнопки для упрощения тестирования
    private JButton plusButton;
    private JButton minusButton;
    private JButton multiplyButton;
    private JButton divideButton;

    public CalculatorGUI() {
        createGUI();
    }

    private void createGUI() {
        frame = new JFrame("Calculator");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);
        frame.setLayout(new GridLayout(5, 2, 10, 10));

        // Input fields
        frame.add(new JLabel("First number:"));
        firstNumberField = new JTextField();
        frame.add(firstNumberField);

        frame.add(new JLabel("Second number:"));
        secondNumberField = new JTextField();
        frame.add(secondNumberField);

        // Buttons
        plusButton = new JButton("+");
        minusButton = new JButton("-");
        multiplyButton = new JButton("*");
        divideButton = new JButton("/");

        // Добавляем кнопки в отдельную панель для лучшего расположения
        JPanel buttonPanel = new JPanel(new GridLayout(1, 4, 5, 5));
        buttonPanel.add(plusButton);
        buttonPanel.add(minusButton);
        buttonPanel.add(multiplyButton);
        buttonPanel.add(divideButton);
        
        frame.add(new JLabel("Operations:"));
        frame.add(buttonPanel);

        // Result field
        frame.add(new JLabel("Result:"));
        resultField = new JTextField();
        resultField.setEditable(false);
        frame.add(resultField);

        // Error label
        errorLabel = new JLabel("");
        errorLabel.setForeground(Color.RED);
        frame.add(errorLabel);
        frame.add(new JLabel()); // Пустая ячейка для выравнивания
    }

    @Override
    public void printResult(double result) {
        resultField.setText(String.valueOf(result));
        errorLabel.setText("");
    }

    @Override
    public void displayError(String message) {
        errorLabel.setText(message);
        resultField.setText("");
    }

    @Override
    public String getFirstArgumentAsString() {
        return firstNumberField.getText().trim();
    }

    @Override
    public String getSecondArgumentAsString() {
        return secondNumberField.getText().trim();
    }

    // Упрощенные методы установки слушателей
    public void setPlusButtonListener(ActionListener listener) {
        plusButton.addActionListener(listener);
    }

    public void setMinusButtonListener(ActionListener listener) {
        minusButton.addActionListener(listener);
    }

    public void setMultiplyButtonListener(ActionListener listener) {
        multiplyButton.addActionListener(listener);
    }

    public void setDivideButtonListener(ActionListener listener) {
        divideButton.addActionListener(listener);
    }

    // Геттеры для тестирования
    public JButton getPlusButton() {
        return plusButton;
    }

    public JButton getMinusButton() {
        return minusButton;
    }

    public JButton getMultiplyButton() {
        return multiplyButton;
    }

    public JButton getDivideButton() {
        return divideButton;
    }

    public JTextField getResultField() {
        return resultField;
    }

    public JLabel getErrorLabel() {
        return errorLabel;
    }

    public void show() {
        frame.setVisible(true);
    }
    public JTextField getFirstNumberField() {
    return firstNumberField;
    }

    public JTextField getSecondNumberField() {
    return secondNumberField;
    }
}