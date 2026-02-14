using System;
namespace LabAB
{
    internal static class Program
    {
        static void Main()
        {
            Console.WriteLine("Лаба по merge-join. Перед запуском смотри DbConfig.ConnectionString.");
            while (true)
            {
                Console.WriteLine();
                Console.WriteLine("1 - Пересоздать таблицы A и B");
                Console.WriteLine("2 - Сгенерировать данные в A и B");
                Console.WriteLine("3 - Создать отсортированные Asrt / Bsrt");
                Console.WriteLine("4 - Стандартный SQL JOIN (AjB_sql)");
                Console.WriteLine("5 - Merge-Join (последовательный, AjB_merge)");
                Console.WriteLine("6 - Merge-Join (параллельный, AjB_merge)");
                Console.WriteLine("0 - Выход");
                Console.Write("Выбор: ");
                string choice = Console.ReadLine();
                Console.WriteLine();
                try
                {
                    switch (choice)
                    {
                        case "1":
                            DbSchema.RecreateTables();
                            Console.WriteLine("Таблицы пересозданы.");
                            break;
                        case "2":
                            ABGenerator.GenerateData(uniqueKeyCount: 1000, minRowsPerKey: 2, maxRowsPerKey: 5);
                            Console.WriteLine("Данные сгенерированы.");
                            break;
                        case "3":
                            TableSorter.CreateSortedCopies();
                            Console.WriteLine("Таблицы Asrt / Bsrt созданы.");
                            break;
                        case "4":
                            var tSql = Benchmark.RunSqlJoin();
                            Console.WriteLine($"SQL JOIN выполнен за {tSql.TotalMilliseconds:F2} мс.");
                            break;
                        case "5":
                            var tMerge = Benchmark.RunMergeSequential();
                            Console.WriteLine($"Merge-Join (последоват.) выполнен за {tMerge.TotalMilliseconds:F2} мс.");
                            break;
                        case "6":
                            var tMergePar = Benchmark.RunMergeParallel();
                            Console.WriteLine($"Merge-Join (паралл.) выполнен за {tMergePar.TotalMilliseconds:F2} мс.");
                            break;
                        case "0":
                            return;
                        default:
                            Console.WriteLine("Неизвестный пункт.");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("ОШИБКА: " + ex.Message);
                }
            }
        }
    }
}