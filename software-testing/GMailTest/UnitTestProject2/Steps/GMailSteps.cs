using Microsoft.VisualStudio.TestTools.UnitTesting;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;
using System;
using TechTalk.SpecFlow;

namespace Gmail.Steps
{
    [Binding]
    public class GMailSteps
    {
        private IWebDriver driver;
        private WebDriverWait wait;

        public GMailSteps()
        {
            var options = new ChromeOptions();
            options.AddArgument("--start-maximized");
            driver = new ChromeDriver(options);
            wait = new WebDriverWait(driver, TimeSpan.FromSeconds(30));
        }

        // Все оптимизированные методы из раздела "Исправленная версия шагов"
        // (код из блока "Исправленная версия шагов")
        
        [Given(@"gmail user is currently logged off")]
        public void GivenGmailUserIsCurrentlyLoggedOff()
        {
            // Реализация
        }

        [Given(@"I have navigated to gmail page")]
        public void GivenIHaveNavigatedToGmailPage()
        {
            // Реализация  
        }

        // ... остальные методы
    }
}