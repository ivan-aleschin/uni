package org.example;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Тестирование регистрации на форуме
 * Используется браузер: Chrome
 */
public class ForumRegistrationTest extends BaseTest {

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--remote-allow-origins=*");
        options.addArguments("--disable-blink-features=AutomationControlled");

        setupDriver(new ChromeDriver(options));
    }

    @Test
    public void testForumRegistration() {
        driver.get("https://demoqa.com/automation-practice-form");

        JavascriptExecutor js = (JavascriptExecutor) driver;

        driver.findElement(By.id("firstName")).sendKeys("Владислав");
        driver.findElement(By.id("lastName")).sendKeys("Казаков");
        driver.findElement(By.id("userEmail")).sendKeys("saschkaproshka04@mail.ru");
        driver.findElement(By.id("userNumber")).sendKeys("0123456789");
        driver.findElement(By.id("currentAddress")).sendKeys("Зеленоград, ул. Юности, 15");

        WebElement maleRadio = driver.findElement(By.xpath("//label[text()='Male']"));
        js.executeScript("arguments[0].click();", maleRadio);

        WebElement sportsCheckbox = driver.findElement(By.xpath("//label[text()='Sports']"));
        js.executeScript("arguments[0].click();", sportsCheckbox);

        WebElement submitButton = driver.findElement(By.id("submit"));
        js.executeScript("arguments[0].click();", submitButton);

        WebElement successMessage = new WebDriverWait(driver, Duration.ofSeconds(10))
                .until(ExpectedConditions.visibilityOfElementLocated(By.id("example-modal-sizes-title-lg")));
        assertTrue(successMessage.isDisplayed(), "Сообщение об успешной регистрации не показано");
    }
}
