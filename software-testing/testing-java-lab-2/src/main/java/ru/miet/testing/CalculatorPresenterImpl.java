package ru.miet.testing;

public class CalculatorPresenterImpl implements CalculatorPresenter {
    private final CalculatorView view;
    private final Calculator calculator;

    public CalculatorPresenterImpl(CalculatorView view, Calculator calculator) {
        this.view = view;
        this.calculator = calculator;
    }

    private Double parseArgument(String arg) {
        try {
            return Double.parseDouble(arg);
        } catch (Exception e) {
            return null;
        }
    }

    private void calculateAndShow(java.util.function.BiFunction<Double, Double, Double> operation) {
        String arg1 = view.getFirstArgumentAsString();
        String arg2 = view.getSecondArgumentAsString();

        Double a = parseArgument(arg1);
        Double b = parseArgument(arg2);

        if (a == null || b == null) {
            view.displayError("Некорректный ввод");
            return;
        }

        try {
            double result = operation.apply(a, b);
            view.printResult(result);
        } catch (ArithmeticException e) {
            view.displayError("Ошибка: " + e.getMessage());
        }
    }

    @Override
    public void onPlusClicked() {
        calculateAndShow(calculator::sum);
    }

    @Override
    public void onMinusClicked() {
        calculateAndShow(calculator::subtract);
    }

    @Override
    public void onDivideClicked() {
        calculateAndShow(calculator::divide);
    }

    @Override
    public void onMultiplyClicked() {
        calculateAndShow(calculator::multiply);
    }
}