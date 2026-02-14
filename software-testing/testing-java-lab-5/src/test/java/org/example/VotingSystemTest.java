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
 * Тестирование системы голосования
 * Используется браузер: Chrome (вместо Edge из-за проблем с сетью)
 */
public class VotingSystemTest extends BaseTest {

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--remote-allow-origins=*");

        setupDriver(new ChromeDriver(options));
    }

    @Test
    public void testVotingSystem() {
        driver.get("https://demoqa.com/checkbox");

        driver.findElement(By.cssSelector(".rct-option-expand-all")).click();

        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        WebElement downloadsCheckbox = wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//span[text()='Downloads']/../span[@class='rct-checkbox']")
        ));

        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(true);", downloadsCheckbox);

        downloadsCheckbox.click();

        WebElement result = driver.findElement(By.id("result"));
        assertTrue(result.getText().contains("downloads"), "Результат голосования не отображается");
    }
}
