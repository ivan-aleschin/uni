using System;
using System.Data.SqlClient;
using System.Diagnostics;

namespace LabAB
{
    internal static class Benchmark
    {
        /// <summary>
        /// Стандартный SQL JOIN (как в QAjB.sql).
        /// </summary>
        public static TimeSpan RunSqlJoin()
        {
            using (var con = DbConfig.CreateConnection())
            {
                con.Open();

                string sql = @"
IF OBJECT_ID('dbo.AjB_sql', 'U') IS NOT NULL DROP TABLE dbo.AjB_sql;
SELECT A.A, SUM(A.B * B.C) AS sBC
INTO AjB_sql
FROM A INNER JOIN B ON A.A = B.A
GROUP BY A.A
ORDER BY A.A;
";

                var sw = Stopwatch.StartNew();
                using (var cmd = new SqlCommand(sql, con))
                {
                    cmd.CommandTimeout = 600;
                    cmd.ExecuteNonQuery();
                }
                sw.Stop();
                return sw.Elapsed;
            }
        }

        public static TimeSpan RunMergeSequential()
        {
            var merge = new MergeAB();
            var sw = Stopwatch.StartNew();
            merge.Init();
            merge.MergeSequential();
            sw.Stop();
            return sw.Elapsed;
        }

        public static TimeSpan RunMergeParallel()
        {
            var merge = new MergeAB();
            var sw = Stopwatch.StartNew();
            merge.Init();
            merge.MergeParallel();
            sw.Stop();
            return sw.Elapsed;
        }
    }
}
