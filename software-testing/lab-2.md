
# Структура

```
project-root/
│
├── src/
│   ├── main/
│   │   └── java/
│   │       └── ru/
│   │           └── miet/
│   │               └── testing/
│   │                   ├── Calculator.java
│   │                   ├── CalculatorView.java
│   │                   ├── CalculatorPresenter.java
│   │                   ├── SimpleCalculator.java           // реализация Calculator
│   │                   ├── CalculatorPresenterImpl.java    // реализация CalculatorPresenter
│   │
│   └── test/
│       └── java/
│           └── ru/
│               └── miet/
│                   └── testing/
│                       ├── SimpleCalculatorTest.java
│                       ├── CalculatorPresenterImplTest.java
│
├── build.gradle  // или pom.xml
└── README.md
```

---
# Код файлов

**SimpleCalculator.java**
```java
package ru.miet.testing;

public class SimpleCalculator implements Calculator {
    @Override
    public double sum(double a, double b) {
        return a + b;
    }

    @Override
    public double subtract(double a, double b) {
        return a - b;
    }

    @Override
    public double multiply(double a, double b) {
        return a * b;
    }

    @Override
    public double divide(double a, double b) {
        if (Math.abs(b) < 1e-8) {
            throw new ArithmeticException("Divider is too close to zero");
        }
        return a / b;
    }
}
```

**CalculatorPresenterImpl.java**

```java
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
```

**SimpleCalculatorTest.java**
```java
package ru.miet.testing;

import org.junit.Test;
import static org.junit.Assert.*;

public class SimpleCalculatorTest {
    private final Calculator calculator = new SimpleCalculator();

    @Test
    public void testSum() {
        assertEquals(5.0, calculator.sum(2, 3), 1e-8);
    }

    @Test
    public void testSubtract() {
        assertEquals(-1.0, calculator.subtract(2, 3), 1e-8);
    }

    @Test
    public void testMultiply() {
        assertEquals(6.0, calculator.multiply(2, 3), 1e-8);
    }

    @Test(expected = ArithmeticException.class)
    public void testDivideByZero() {
        calculator.divide(1, 0);
    }

    @Test
    public void testDivide() {
        assertEquals(2.0, calculator.divide(6, 3), 1e-8);
    }
}
```

**CalculatorPresenterImplTest**
```java
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
```

**CalculatorView**
```java
package ru.miet.testing;

public interface CalculatorView {

    /**
     * Отображает результат вычисления
     */
    void printResult(double result);

    /**
     * Показывает ошибку, например деление на 0, пустые аргументы и прочее
     */
    void displayError(String message);

    /**
     * Возвращает значение, введенное в поле первого аргументы
     */
    String getFirstArgumentAsString();

    /**
     * Возвращает значение, введенное в поле второго аргументы
     */
    String getSecondArgumentAsString();
}

```

**CalculatorPresenter.java**
```java
package ru.miet.testing;

public interface CalculatorPresenter {
    /**
     * Вызывается формой в тот момент, когда пользователь нажал на кнопку '+'
     */
    void onPlusClicked();

    /**
     * Вызывается формой в тот момент, когда пользователь нажал на кнопку '-'
     */
    void onMinusClicked();

    /**
     * Вызывается формой в тот момент, когда пользователь нажал на кнопку '/'
     */
    void onDivideClicked();

    /**
     * Вызывается формой в тот момент, когда пользователь нажал на кнопку '*'
     */
    void onMultiplyClicked();
}

```

**Calculator.java**
```java
package ru.miet.testing;

public interface Calculator {

    /**
     * Вычисляет сумму двух чисел
     */
    double sum(double a, double b);


    /**
     * Вычисляет разность двух чисел a - b
     */
    double subtract(double a, double b);

    /**
     * Вычисляет произведение двух чисел
     */
    double multiply(double a, double b);

    /**
     * Вычисляет отношение числа а к числу b.
     * Должен выбросить {@link java.lang.ArithmeticException} если |b| < 10e-8
     */
    double divide(double a, double b);
}

```

**build.gradle**
```
plugins {
    id 'java'
}

group = 'ru.miet'
version = '1.0-SNAPSHOT'

repositories {
    mavenCentral()
}

dependencies {
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.mockito:mockito-core:5.2.0'
}
```

---

# Контрольные вопросы

**1. В чем отличие приемочного тестирования от системного?**  
*Приемочное тестирование* — это финальная проверка, проводится заказчиком или представителями пользователя, чтобы убедиться, что система соответствует бизнес-требованиям и готова к эксплуатации.  
*Системное тестирование* — это комплексная проверка всей системы как единого целого, проводится командой тестировщиков для проверки соответствия техническим требованиям и спецификациям.

---

**2. Что такое моки и стабы?**  
*Моки (Mock)* — это объекты-заглушки, которые имитируют поведение настоящих объектов и позволяют проверять взаимодействие между компонентами.  
*Стабы (Stub)* — это простые реализации интерфейсов, возвращающие заранее определённые значения, используемые для изоляции тестируемых компонентов.

---

**3. Как осуществляется планирование тестов?**  
Планирование тестов включает: анализ требований, определение стратегии тестирования, выбор методов и инструментов, оценку ресурсов и сроков, составление тест-плана (описание объёмов, задач, критериев качества, расписания тестирования).

---

**4. Какие правила организации тестов вы знаете?**  
- Каждый тест должен быть независимым.
- Использовать понятные и осмысленные имена тестов.
- Группировать тесты по типу (юнит, интеграционные и т.д.).
- Использовать шаблон Arrange-Act-Assert.
- Изолировать внешние зависимости с помощью моков/стабов.
- Не допускать дублирования кода в тестах.

---

**5. Что за шаблон Arrange-Act-Assert?**  
Это структура теста:
- **Arrange** — подготовка данных и окружения.
- **Act** — выполнение действия (вызов тестируемого метода).
- **Assert** — проверка результатов.

---

**6. Какие преимущества применения unit-тестирования?**  
- Быстро выявлять ошибки на ранних этапах.
- Упрощение рефакторинга и сопровождения кода.
- Автоматизация проверки изменений.
- Повышение качества и надёжности ПО.
- Улучшение архитектуры (код становится более модульным).

---

**7. Что такое тестовое покрытие?**  
Тестовое покрытие — это метрика, отражающая, какая часть исходного кода была выполнена во время тестирования (например, покрытие строк кода, ветвлений, условий). Используется для оценки полноты тестирования.

