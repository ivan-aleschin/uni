using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using ParallelJoinLab.Models;

namespace ParallelJoinLab
{
    public class JoinResult
    {
        public Student Student { get; set; }
        public Course Course { get; set; }
        public string JoinKey => Student.Key; // Используем Student.Key как ключ соединения
        
        public override string ToString()
        {
            return $"[{JoinKey}] Student: {Student.FirstName} {Student.LastName}, Course: {Course.CourseName}";
        }
    }

    public class ParallelJoin
    {
        // Стандартный Join (последовательный)
        public static List<JoinResult> StandardJoin(List<Student> students, List<Course> courses)
        {
            var result = new List<JoinResult>();
            
            // Простой вложенный цикл - аналог SQL JOIN
            foreach (var student in students)
            {
                foreach (var course in courses)
                {
                    if (student.Key == course.Key) // Соединение по ключу
                    {
                        result.Add(new JoinResult { Student = student, Course = course });
                    }
                }
            }
            
            return result;
        }

        // Merge Join алгоритм (аналогично NonStrCMrg.cs)
        public static List<JoinResult> MergeJoin(List<Student> students, List<Course> courses)
        {
            var result = new List<JoinResult>();
            
            // Предполагаем, что обе коллекции отсортированы по ключу
            int i = 0, j = 0;
            
            while (i < students.Count && j < courses.Count)
            {
                var student = students[i];
                var course = courses[j];
                
                int comparison = string.Compare(student.Key, course.Key, StringComparison.Ordinal);
                
                if (comparison == 0)
                {
                    // Ключи совпадают - добавляем в результат
                    result.Add(new JoinResult { Student = student, Course = course });
                    
                    // Обработка возможных дубликатов в students
                    int k = i + 1;
                    while (k < students.Count && students[k].Key == student.Key)
                    {
                        result.Add(new JoinResult { Student = students[k], Course = course });
                        k++;
                    }
                    
                    // Обработка возможных дубликатов в courses  
                    int l = j + 1;
                    while (l < courses.Count && courses[l].Key == course.Key)
                    {
                        result.Add(new JoinResult { Student = student, Course = courses[l] });
                        l++;
                    }
                    
                    i++;
                    j++;
                }
                else if (comparison < 0)
                {
                    i++; // student.Key < course.Key
                }
                else
                {
                    j++; // student.Key > course.Key
                }
            }
            
            return result;
        }

        // Параллельная версия Merge Join
        public static List<JoinResult> ParallelMergeJoin(List<Student> students, List<Course> courses)
        {
            var result = new List<JoinResult>();
            object lockObject = new object();

            // Распараллеливание обработки - разбиваем студентов на части
            Parallel.ForEach(Partitioner.Create(0, students.Count), range =>
            {
                var localResults = new List<JoinResult>();
                
                for (int i = range.Item1; i < range.Item2; i++)
                {
                    var student = students[i];
                    
                    // Бинарный поиск в отсортированном списке курсов
                    int courseIndex = BinarySearch(courses, student.Key);
                    if (courseIndex >= 0)
                    {
                        // Нашли совпадение - добавляем все курсы с таким ключом
                        int left = courseIndex;
                        while (left >= 0 && courses[left].Key == student.Key)
                        {
                            localResults.Add(new JoinResult { Student = student, Course = courses[left] });
                            left--;
                        }
                        
                        int right = courseIndex + 1;
                        while (right < courses.Count && courses[right].Key == student.Key)
                        {
                            localResults.Add(new JoinResult { Student = student, Course = courses[right] });
                            right++;
                        }
                    }
                }
                
                // Безопасное добавление результатов из разных потоков
                lock (lockObject)
                {
                    result.AddRange(localResults);
                }
            });

            return result;
        }

        // Вспомогательный метод бинарного поиска
        private static int BinarySearch(List<Course> courses, string key)
        {
            int left = 0;
            int right = courses.Count - 1;
            
            while (left <= right)
            {
                int mid = left + (right - left) / 2;
                int comparison = string.Compare(courses[mid].Key, key, StringComparison.Ordinal);
                
                if (comparison == 0)
                    return mid;
                else if (comparison < 0)
                    left = mid + 1;
                else
                    right = mid - 1;
            }
            
            return -1;
        }

        public static (TimeSpan standardTime, TimeSpan mergeTime, TimeSpan parallelTime, 
                      List<JoinResult> standardResult, List<JoinResult> mergeResult, List<JoinResult> parallelResult) 
            CompareJoins(List<Student> students, List<Course> courses)
        {
            // Тестирование стандартного Join
            var stopwatch = Stopwatch.StartNew();
            var standardResult = StandardJoin(students, courses);
            stopwatch.Stop();
            var standardTime = stopwatch.Elapsed;

            // Тестирование Merge Join
            stopwatch.Restart();
            var mergeResult = MergeJoin(students, courses);
            stopwatch.Stop();
            var mergeTime = stopwatch.Elapsed;

            // Тестирование параллельного Merge Join
            stopwatch.Restart();
            var parallelResult = ParallelMergeJoin(students, courses);
            stopwatch.Stop();
            var parallelTime = stopwatch.Elapsed;

            return (standardTime, mergeTime, parallelTime, standardResult, mergeResult, parallelResult);
        }
    }

    // Вспомогательный класс для разделения данных
    public static class Partitioner
    {
        public static IEnumerable<Tuple<int, int>> Create(int fromInclusive, int toExclusive)
        {
            int rangeSize = (toExclusive - fromInclusive) / Environment.ProcessorCount;
            for (int i = 0; i < Environment.ProcessorCount; i++)
            {
                int start = i * rangeSize + fromInclusive;
                int end = (i == Environment.ProcessorCount - 1) ? toExclusive : start + rangeSize;
                yield return Tuple.Create(start, end);
            }
        }
    }
}