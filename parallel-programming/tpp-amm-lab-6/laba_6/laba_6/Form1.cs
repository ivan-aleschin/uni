using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace laba_6
{
    public partial class Form1 : Form
    {
        private CancellationTokenSource? _cancellationTokenSource;
        private readonly object _lockObject = new object();
        private volatile bool _isRunning = false;
        private long _totalMemoryAllocated = 0;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            cmbThreads.SelectedIndex = 0;
            UpdateMemoryUsage();
        }

        private async void BtnStart_Click(object sender, EventArgs e)
        {
            if (_isRunning)
            {
                _cancellationTokenSource?.Cancel();
                return;
            }

            try
            {
                _isRunning = true;
                btnStart.Text = "Остановить";
                btnProfile.Enabled = false;
                _cancellationTokenSource = new CancellationTokenSource();

                if (!int.TryParse(txtMaxNumber.Text, out int maxNumber))
                {
                    MessageBox.Show("Введите корректное число для N", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                int threadCount = GetThreadCount();

                await RunFactorizationAsync(maxNumber, threadCount, _cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                txtStatus.Text = "Операция отменена";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                _isRunning = false;
                btnStart.Text = "Запуск вычислений";
                btnProfile.Enabled = true;
            }
        }

        private void BtnProfile_Click(object sender, EventArgs e)
        {
            MessageBox.Show("Для профилирования:\n1. В меню выберите Analyze -> Launch Performance Wizard\n2. Выберите соответствующий метод профилирования\n3. Запустите вычисления через интерфейс",
                "Инструкция по профилированию", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        private int GetThreadCount()
        {
            if (cmbThreads.SelectedIndex == 0) return Environment.ProcessorCount;

            if (cmbThreads.SelectedItem != null && int.TryParse(cmbThreads.SelectedItem.ToString(), out int threads))
                return threads;

            return Environment.ProcessorCount;
        }

        private async Task RunFactorizationAsync(int maxNumber, int threadCount, CancellationToken cancellationToken)
        {
            txtDetails.Clear();
            txtExamples.Clear();
            txtThreadStats.Clear();
            _totalMemoryAllocated = 0;

            var stopwatch = Stopwatch.StartNew();

            try
            {
                var results = await Task.Run(() =>
                    FactorizeNumbersParallel(maxNumber, threadCount, cancellationToken), cancellationToken);

                stopwatch.Stop();
                DisplayResults(results, stopwatch.ElapsedMilliseconds, maxNumber);
            }
            catch (OperationCanceledException)
            {
                txtStatus.Text = "Вычисления отменены";
            }
        }

        private Dictionary<int, List<int>> FactorizeNumbersParallel(int maxNumber, int threadCount, CancellationToken cancellationToken)
        {
            var results = new Dictionary<int, List<int>>();
            var threadStats = new int[threadCount];
            long totalMemory = 0;
            int processed = 0;

            Parallel.For(1, maxNumber + 1, new ParallelOptions
            {
                MaxDegreeOfParallelism = threadCount,
                CancellationToken = cancellationToken
            }, (number) =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                // Получаем индекс потока
                int threadIndex = Thread.CurrentThread.ManagedThreadId % threadCount;

                // Имитация различной нагрузки для разных чисел
                if (number % 100 == 0) Thread.SpinWait(100);

                var factors = Factorize(number);
                Interlocked.Increment(ref threadStats[threadIndex]);

                // Блокировка для потокобезопасного доступа
                lock (_lockObject)
                {
                    results[number] = factors;
                    totalMemory += factors.Count * sizeof(int);
                    processed++;

                    // Обновление прогресса каждые 1000 чисел
                    if (processed % 1000 == 0)
                    {
                        int percent = (int)((double)processed / maxNumber * 100);

                        // Обновление в UI потоке
                        if (!this.IsDisposed)
                        {
                            this.Invoke(new Action(() =>
                            {
                                progressBar.Value = Math.Min(percent, 100);
                                txtProgress.Text = $"Выполнено: {percent}%";
                                _totalMemoryAllocated = totalMemory;
                                UpdateMemoryUsage();
                                UpdateThreadStats(threadStats);
                            }));
                        }
                    }
                }
            });

            return results;
        }

        private List<int> Factorize(int number)
        {
            var factors = new List<int>();
            int n = number;

            if (number == 1)
            {
                factors.Add(1);
                return factors;
            }

            // Оптимизированный алгоритм разложения
            while (n % 2 == 0)
            {
                factors.Add(2);
                n /= 2;
            }

            for (int i = 3; i * i <= n; i += 2)
            {
                while (n % i == 0)
                {
                    factors.Add(i);
                    n /= i;
                }
            }

            if (n > 1)
            {
                factors.Add(n);
            }

            return factors;
        }

        private void UpdateThreadStats(int[] threadStats)
        {
            var stats = new StringBuilder();
            stats.AppendLine($"Всего потоков: {threadStats.Length}");
            stats.AppendLine("Обработано чисел по потокам:");

            for (int i = 0; i < threadStats.Length; i++)
            {
                stats.AppendLine($"Поток {i + 1}: {threadStats[i]} чисел");
            }

            txtThreadStats.Text = stats.ToString();
        }

        private void UpdateMemoryUsage()
        {
            var memory = GC.GetTotalMemory(false) / 1024 / 1024;
            txtMemory.Text = $"Память: {memory} MB | Выделено: {_totalMemoryAllocated / 1024} KB";
        }

        private void DisplayResults(Dictionary<int, List<int>> results, long elapsedMs, int maxNumber)
        {
            txtResults.Text = $"Время: {elapsedMs} мс | Обработано: {results.Count}/{maxNumber} чисел";

            // Показываем примеры разложений
            var examples = new StringBuilder();
            for (int i = 1; i <= Math.Min(20, maxNumber); i++)
            {
                if (results.ContainsKey(i))
                {
                    examples.AppendLine($"{i} = {string.Join(" × ", results[i])}");
                }
            }
            txtExamples.Text = examples.ToString();

            // Детальная информация
            var details = new StringBuilder();
            details.AppendLine("=== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ВЫПОЛНЕНИИ ===");
            details.AppendLine($"Общее время: {elapsedMs} мс");
            details.AppendLine($"Обработано чисел: {results.Count}");
            details.AppendLine($"Максимальное число: {maxNumber}");
            details.AppendLine($"Потоков использовано: {GetThreadCount()}");

            long totalFactors = 0;
            foreach (var result in results)
            {
                totalFactors += result.Value.Count;
            }

            details.AppendLine($"Всего множителей: {totalFactors}");
            details.AppendLine($"Память под результаты: {_totalMemoryAllocated / 1024} KB");
            details.AppendLine();

            // Статистика по размерам разложений
            var sizeGroups = results.GroupBy(r => r.Value.Count)
                                   .OrderBy(g => g.Key)
                                   .Take(10);

            details.AppendLine("Распределение по количеству множителей:");
            foreach (var group in sizeGroups)
            {
                details.AppendLine($"  {group.Key} множителей: {group.Count()} чисел");
            }

            txtDetails.Text = details.ToString();
            txtStatus.Text = "Вычисления завершены";
            progressBar.Value = 100;
            txtProgress.Text = "Завершено: 100%";
        }
    }
}