package org.example;

import org.junit.jupiter.api.AfterEach;
import org.openqa.selenium.WebDriver;
import java.time.Duration;

public abstract class BaseTest {
    protected WebDriver driver;

    protected void setupDriver(WebDriver webDriver) {
        this.driver = webDriver;
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
