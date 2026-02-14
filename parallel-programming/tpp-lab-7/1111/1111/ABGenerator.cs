using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;

namespace LabAB
{
    internal static class ABGenerator
    {
        /// <summary>
        /// Генерирует данные в таблицы A и B.
        /// uniqueKeyCount – сколько разных ключей,
        /// min/maxRowsPerKey – минимум/максимум записей на каждый ключ (>=2).
        /// </summary>
        public static void GenerateData(int uniqueKeyCount, int minRowsPerKey = 2, int maxRowsPerKey = 5)
        {
            if (uniqueKeyCount <= 0) throw new ArgumentOutOfRangeException(nameof(uniqueKeyCount));
            if (minRowsPerKey < 2) throw new ArgumentOutOfRangeException(nameof(minRowsPerKey));
            if (maxRowsPerKey < minRowsPerKey) throw new ArgumentOutOfRangeException(nameof(maxRowsPerKey));

            var rand = new Random();

            var keys = GenerateKeys(uniqueKeyCount, rand);

            // Таблица A
            DataTable wA = new DataTable();
            wA.Columns.Add("A", typeof(string));
            wA.Columns.Add("B", typeof(int));
            wA.Columns.Add("D1", typeof(int));
            wA.Columns.Add("D2", typeof(double));

            // Таблица B
            DataTable wB = new DataTable();
            wB.Columns.Add("A", typeof(string));
            wB.Columns.Add("C", typeof(int));
            wB.Columns.Add("E1", typeof(int));
            wB.Columns.Add("E2", typeof(double));

            foreach (var key in keys)
            {
                int countA = rand.Next(minRowsPerKey, maxRowsPerKey + 1);
                for (int i = 0; i < countA; i++)
                {
                    wA.Rows.Add(
                        key,
                        rand.Next(0, 10),         // B
                        rand.Next(0, 100),        // D1
                        rand.NextDouble() * 100.0 // D2
                    );
                }

                int countB = rand.Next(minRowsPerKey, maxRowsPerKey + 1);
                for (int i = 0; i < countB; i++)
                {
                    wB.Rows.Add(
                        key,
                        rand.Next(0, 10),         // C
                        rand.Next(0, 100),        // E1
                        rand.NextDouble() * 100.0 // E2
                    );
                }
            }

            using (var con = DbConfig.CreateConnection())
            {
                con.Open();

                using (var bulkA = new SqlBulkCopy(con))
                {
                    bulkA.DestinationTableName = "dbo.A";
                    bulkA.ColumnMappings.Add("A", "A");
                    bulkA.ColumnMappings.Add("B", "B");
                    bulkA.ColumnMappings.Add("D1", "D1");
                    bulkA.ColumnMappings.Add("D2", "D2");
                    bulkA.BatchSize = wA.Rows.Count;
                    bulkA.BulkCopyTimeout = 600;
                    bulkA.WriteToServer(wA);
                }

                using (var bulkB = new SqlBulkCopy(con))
                {
                    bulkB.DestinationTableName = "dbo.B";
                    bulkB.ColumnMappings.Add("A", "A");
                    bulkB.ColumnMappings.Add("C", "C");
                    bulkB.ColumnMappings.Add("E1", "E1");
                    bulkB.ColumnMappings.Add("E2", "E2");
                    bulkB.BatchSize = wB.Rows.Count;
                    bulkB.BulkCopyTimeout = 600;
                    bulkB.WriteToServer(wB);
                }
            }
        }

        private static List<string> GenerateKeys(int count, Random rand)
        {
            var result = new List<string>(count);
            var used = new HashSet<string>(StringComparer.Ordinal);

            while (result.Count < count)
            {
                string key = GenerateKey(rand);
                if (used.Add(key))
                    result.Add(key);
            }

            return result;
        }

        // Ключ – строка длиной L из букв 'A'/'B'
        private static string GenerateKey(Random rand)
        {
            char[] buf = new char[DbSchema.KeyLength];

            for (int i = 0; i < buf.Length; i++)
                buf[i] = rand.Next(2) == 0 ? 'A' : 'B';

            return new string(buf);
        }
    }
}
