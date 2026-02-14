using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.Threading;
using System.Diagnostics;
using System.Threading.Tasks;

namespace Gmail.Tests
{
    [TestClass]
    public class GmailLoadTests
    {
        [TestMethod]
        public void LoadTest_MultipleParallelLogins()
        {
            // Код из раздела "Нагрузочные тесты"
        }

        [TestMethod]
        public void PerformanceTest_EmailSending()
        {
            // Код из раздела "Нагрузочные тесты"  
        }
    }
}