using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using ParallelJoinLab.Models;

namespace ParallelJoinLab
{
    public partial class MainForm : Form  // УБРАТЬ 'private' отсюда!
    {
        private DatabaseHelper _dbHelper;
        private List<JoinResult> _currentResults;

        public MainForm()
        {
            InitializeComponent();
            _dbHelper = new DatabaseHelper();
        }

        private void btnGenerateData_Click(object sender, EventArgs e)
        {
            try
            {
                var studentCount = string.IsNullOrEmpty(txtStudentCount.Text) ? 10000 : int.Parse(txtStudentCount.Text);
                var courseCount = string.IsNullOrEmpty(txtCourseCount.Text) ? 10000 : int.Parse(txtCourseCount.Text);
                
                _dbHelper.GenerateTestData(studentCount, courseCount);
                MessageBox.Show($"Тестовые данные сгенерированы успешно! Студентов: {studentCount}, Курсов: {courseCount}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}");
            }
        }

        private void btnCreateSorted_Click(object sender, EventArgs e)
        {
            try
            {
                _dbHelper.CreateSortedTables();
                MessageBox.Show("Отсортированные таблицы созданы!");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}");
            }
        }

        private void btnCompareJoins_Click(object sender, EventArgs e)
        {
            try
            {
                var students = _dbHelper.GetStudents(true);
                var courses = _dbHelper.GetCourses(true);

                lblStatus.Text = "Выполняется сравнение алгоритмов...";
                Application.DoEvents();

                var (standardTime, mergeTime, parallelTime, standardResult, mergeResult, parallelResult) = 
                    ParallelJoin.CompareJoins(students, courses);

                _currentResults = parallelResult;

                // Обновление UI с результатами
                lblStandardTime.Text = $"Стандартный Join: {standardTime.TotalMilliseconds:F2} мс";
                lblMergeTime.Text = $"Merge Join: {mergeTime.TotalMilliseconds:F2} мс";
                lblParallelTime.Text = $"Параллельный Merge: {parallelTime.TotalMilliseconds:F2} мс";
                
                lblStandardCount.Text = $"Найдено: {standardResult.Count}";
                lblMergeCount.Text = $"Найдено: {mergeResult.Count}";
                lblParallelCount.Text = $"Найдено: {parallelResult.Count}";

                // Расчет ускорения
                double speedupVsStandard = standardTime.TotalMilliseconds / parallelTime.TotalMilliseconds;
                double speedupVsMerge = mergeTime.TotalMilliseconds / parallelTime.TotalMilliseconds;
                
                lblSpeedup.Text = $"Ускорение vs Standard: {speedupVsStandard:F2}x\n" +
                                 $"Ускорение vs Merge: {speedupVsMerge:F2}x";

                // Проверка корректности результатов
                bool resultsValid = standardResult.Count == mergeResult.Count && 
                                   mergeResult.Count == parallelResult.Count;
                
                lblValidation.Text = resultsValid ? "✓ Результаты корректны" : "⚠ Расхождение в результатах";

                // Показ первых результатов
                listBoxResults.Items.Clear();
                listBoxResults.Items.Add($"Всего найдено совпадений: {parallelResult.Count}");
                listBoxResults.Items.Add("Первые 10 результатов:");
                
                foreach (var result in parallelResult.Take(10))
                {
                    listBoxResults.Items.Add(result.ToString());
                }

                // Анализ дубликатов ключей
                _dbHelper.AnalyzeDuplicates();

                lblStatus.Text = "Готово";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}");
                lblStatus.Text = "Ошибка";
            }
        }

        private void btnShowDuplicates_Click(object sender, EventArgs e)
        {
            try
            {
                var students = _dbHelper.GetStudents();
                var courses = _dbHelper.GetCourses();

                // Анализ дубликатов ключей
                var studentGroups = students.GroupBy(s => s.Key)
                    .Where(g => g.Count() > 1)
                    .OrderByDescending(g => g.Count())
                    .Take(5);

                var courseGroups = courses.GroupBy(c => c.Key)
                    .Where(g => g.Count() > 1)
                    .OrderByDescending(g => g.Count())
                    .Take(5);

                string message = "Студенты с дубликатами ключей:\n";
                foreach (var group in studentGroups)
                {
                    message += $"Ключ '{group.Key}': {group.Count()} записей\n";
                }

                message += "\nКурсы с дубликатами ключей:\n";
                foreach (var group in courseGroups)
                {
                    message += $"Ключ '{group.Key}': {group.Count()} записей\n";
                }

                if (!studentGroups.Any() && !courseGroups.Any())
                {
                    message = "Дубликаты ключей не найдены. Увеличьте количество записей для появления дубликатов.";
                }

                MessageBox.Show(message, "Анализ дубликатов");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}");
            }
        }
    }
}