package ru.miet.testing;

import javax.swing.*;

public class Main {
    public static void main(String[] args) {
        // Запускаем в EDT (Event Dispatch Thread) как того требуют правила Swing
        SwingUtilities.invokeLater(() -> {
            // Создаем view и presenter
            CalculatorGUI view = new CalculatorGUI();
            CalculatorPresenter presenter = new CalculatorPresenterImpl(view);
            
            // Устанавливаем связь между view и presenter
            view.setPlusButtonListener(e -> presenter.onPlusClicked());
            view.setMinusButtonListener(e -> presenter.onMinusClicked());
            view.setMultiplyButtonListener(e -> presenter.onMultiplyClicked());
            view.setDivideButtonListener(e -> presenter.onDivideClicked());
            
            // Показываем интерфейс
            view.show();
        });
    }
}