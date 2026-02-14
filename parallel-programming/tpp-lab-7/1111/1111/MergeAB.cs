using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Threading.Tasks;

namespace LabAB
{
    internal class MergeAB
    {
        private struct Bucket
        {
            public string Key;
            public List<int> Bs;   // значения поля B для текущего ключа
        }

        private SqlConnection conA, conB, conRes;
        private SqlCommand cmdA, cmdB;
        private SqlDataReader readA, readB;
        private SqlBulkCopy bcRes;
        private DataTable wRes;

        private Bucket bucket;
        private bool hasA;

        public void Init()
        {
            conA = DbConfig.CreateConnection();
            conB = DbConfig.CreateConnection();
            conRes = DbConfig.CreateConnection();

            conA.Open();
            conB.Open();
            conRes.Open();

            // Готовим таблицу результата AjB_merge
            string prepareSql = @"
IF OBJECT_ID('dbo.AjB_merge', 'U') IS NOT NULL DROP TABLE dbo.AjB_merge;
CREATE TABLE dbo.AjB_merge
(
    A   NCHAR(" + DbSchema.KeyLength + @") NOT NULL,
    sBC FLOAT NOT NULL
);";

            using (var cmd = new SqlCommand(prepareSql, conRes))
            {
                cmd.ExecuteNonQuery();
            }

            cmdA = new SqlCommand("SELECT A, B FROM Asrt ORDER BY A;", conA);
            cmdB = new SqlCommand("SELECT A, C FROM Bsrt ORDER BY A;", conB);

            readA = cmdA.ExecuteReader();
            readB = cmdB.ExecuteReader();

            wRes = new DataTable();
            wRes.Columns.Add("A", typeof(string));
            wRes.Columns.Add("sBC", typeof(double));

            bcRes = new SqlBulkCopy(conRes);
            bcRes.DestinationTableName = "dbo.AjB_merge";
            bcRes.ColumnMappings.Add("A", "A");
            bcRes.ColumnMappings.Add("sBC", "sBC");
        }

        private static int KeyCompare(string bucketKey, string otherKey)
        {
            return string.Compare(bucketKey, otherKey, StringComparison.Ordinal);
        }

        /// <summary>
        /// Загружает очередной «черпак» из Asrt (все строки с текущим ключом).
        /// </summary>
        private bool Scoop()
        {
            bucket.Bs = new List<int>();
            bucket.Key = null;

            if (!hasA)
                return false;

            string key = readA.GetString(0).TrimEnd();
            bucket.Key = key;

            // Собираем все строки с этим ключом
            do
            {
                int bVal = readA.GetInt32(1);
                bucket.Bs.Add(bVal);
                hasA = readA.Read();
            }
            while (hasA && readA.GetString(0).TrimEnd() == key);

            return true;
        }

        private void FlushResultRow(string key, double sum)
        {
            if (key == null) return;
            var row = wRes.NewRow();
            row["A"] = key;
            row["sBC"] = sum;
            wRes.Rows.Add(row);
        }

        /// <summary>
        /// Основной merge-алгоритм. 
        /// parallel=false — обычный, parallel=true — параллельная обработка черпака.
        /// </summary>
        private void MergeInternal(bool parallel)
        {
            if (readA == null || readB == null)
                throw new InvalidOperationException("Сначала вызови Init().");

            hasA = readA.Read();
            bool nonexhaust = Scoop();   // загружаем первый черпак
            bool hasB = readB.Read();

            string currentKey = null;
            double currentSum = 0.0;

            while (nonexhaust && hasB)
            {
                string keyB = readB.GetString(0).TrimEnd();
                int cmp = KeyCompare(bucket.Key, keyB);

                if (cmp < 0)
                {
                    // ключ черпака меньше — двигаем ведущую таблицу (новый черпак)
                    nonexhaust = Scoop();
                }
                else if (cmp > 0)
                {
                    // ключ в Bsrt меньше — двигаем ведомую таблицу
                    hasB = readB.Read();
                }
                else
                {
                    // совпадение ключей — совместная обработка текущего черпака и строки Bsrt
                    int cVal = readB.GetInt32(1);

                    double localSum = 0.0;

                    if (parallel)
                    {
                        object lockObj = new object();
                        Parallel.ForEach(bucket.Bs, bVal =>
                        {
                            double prod = bVal * cVal;
                            lock (lockObj)
                            {
                                localSum += prod;
                            }
                        });
                    }
                    else
                    {
                        foreach (int bVal in bucket.Bs)
                        {
                            localSum += bVal * cVal;
                        }
                    }

                    if (currentKey == null || currentKey != keyB)
                    {
                        // закрываем предыдущий ключ
                        FlushResultRow(currentKey, currentSum);
                        currentKey = keyB;
                        currentSum = localSum;
                    }
                    else
                    {
                        currentSum += localSum;
                    }

                    // следующая строка Bsrt
                    hasB = readB.Read();
                }
            }

            // финальный ключ
            FlushResultRow(currentKey, currentSum);

            if (wRes.Rows.Count > 0)
            {
                bcRes.BatchSize = wRes.Rows.Count;
                bcRes.BulkCopyTimeout = 600;
                bcRes.WriteToServer(wRes);
            }

            bcRes.Close();
            readA.Close();
            readB.Close();
            conA.Close();
            conB.Close();
            conRes.Close();
        }

        public void MergeSequential()
        {
            MergeInternal(parallel: false);
        }

        public void MergeParallel()
        {
            MergeInternal(parallel: true);
        }
    }
}
