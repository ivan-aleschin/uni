package ru.miet.testing;

public class CalculatorPresenterImpl implements CalculatorPresenter {
    private CalculatorView view;
    private Calculator calculator;

    public CalculatorPresenterImpl(CalculatorView view) {
        this.view = view;
        this.calculator = new CalculatorImpl();
    }

    private void performOperation(char operation) {
        try {
            String firstArgStr = view.getFirstArgumentAsString();
            String secondArgStr = view.getSecondArgumentAsString();
            
            // Проверка на пустые поля
            if (firstArgStr.isEmpty() || secondArgStr.isEmpty()) {
                view.displayError("Please enter both numbers");
                return;
            }
            
            double a = Double.parseDouble(firstArgStr);
            double b = Double.parseDouble(secondArgStr);
            double result = 0;

            switch (operation) {
                case '+':
                    result = calculator.sum(a, b);
                    break;
                case '-':
                    result = calculator.subtract(a, b);
                    break;
                case '*':
                    result = calculator.multiply(a, b);
                    break;
                case '/':
                    result = calculator.divide(a, b);
                    break;
            }

            view.printResult(result);
        } catch (NumberFormatException e) {
            view.displayError("Please enter valid numbers");
        } catch (ArithmeticException e) {
            view.displayError(e.getMessage());
        } catch (Exception e) {
            view.displayError("An error occurred: " + e.getMessage());
        }
    }

    @Override
    public void onPlusClicked() {
        performOperation('+');
    }

    @Override
    public void onMinusClicked() {
        performOperation('-');
    }

    @Override
    public void onDivideClicked() {
        performOperation('/');
    }

    @Override
    public void onMultiplyClicked() {
        performOperation('*');
    }
}