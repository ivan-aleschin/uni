package org.example;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Тестирование телефонного справочника
 * Используется браузер: Chrome (вместо Firefox, т.к. Firefox не установлен)
 */
public class PhoneDirectoryTest extends BaseTest {

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--remote-allow-origins=*");

        setupDriver(new ChromeDriver(options));
    }

    @Test
    public void testPhoneDirectorySearch() {
        driver.get("https://demoqa.com/webtables");

        driver.findElement(By.id("addNewRecordButton")).click();
        driver.findElement(By.id("firstName")).sendKeys("Владислав");
        driver.findElement(By.id("lastName")).sendKeys("Казаков");
        driver.findElement(By.id("userEmail")).sendKeys("saschkaproshka04@mail.ru");
        driver.findElement(By.id("age")).sendKeys("19");
        driver.findElement(By.id("salary")).sendKeys("50000");
        driver.findElement(By.id("department")).sendKeys("IT");
        driver.findElement(By.id("submit")).click();

        WebElement searchBox = driver.findElement(By.id("searchBox"));
        searchBox.sendKeys("Владислав");

        List<WebElement> rows = driver.findElements(By.cssSelector(".rt-tr-group"));
        boolean found = false;
        for (WebElement row : rows) {
            if (row.getText().contains("Владислав") && row.getText().contains("Казаков")) {
                found = true;
                break;
            }
        }
        assertTrue(found, "Запись не найдена в телефонном справочнике");
    }
}