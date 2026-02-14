package org.example;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Тестирование поиска
 * Используется браузер: Chrome
 */
public class SearchTest extends BaseTest {

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--remote-allow-origins=*");

        setupDriver(new ChromeDriver(options));
    }

    @Test
    public void testSearchFunctionality() {
        driver.get("https://demoqa.com/books");

        WebElement searchBox = driver.findElement(By.id("searchBox"));
        assertTrue(searchBox.isDisplayed(), "Поисковая строка не найдена");

        searchBox.sendKeys("Java");
        searchBox.sendKeys(Keys.ENTER);

        new WebDriverWait(driver, Duration.ofSeconds(5))
                .until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".rt-table")));

        List<WebElement> books = driver.findElements(By.cssSelector(".rt-tr-group"));
        assertTrue(books.size() > 0, "Книги не найдены");
        assertTrue(books.get(0).getText().contains("Java"), "Неверные результаты поиска");

        searchBox.clear();
        searchBox.sendKeys(Keys.ENTER);

        List<WebElement> allBooks = driver.findElements(By.cssSelector(".rt-tr-group"));
        assertTrue(allBooks.size() > 1, "Поиск не очищается");
    }
}
