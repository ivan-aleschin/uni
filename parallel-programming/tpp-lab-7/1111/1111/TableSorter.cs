using System.Data.SqlClient;

namespace LabAB
{
    internal static class TableSorter
    {
        public static void CreateSortedCopies()
        {
            using (var con = DbConfig.CreateConnection())
            {
                con.Open();

                string sql = @"
IF OBJECT_ID('dbo.Asrt', 'U') IS NOT NULL DROP TABLE dbo.Asrt;
IF OBJECT_ID('dbo.Bsrt', 'U') IS NOT NULL DROP TABLE dbo.Bsrt;

SELECT * INTO Asrt FROM A ORDER BY A;
SELECT * INTO Bsrt FROM B ORDER BY A;
";

                using (var cmd = new SqlCommand(sql, con))
                {
                    cmd.ExecuteNonQuery();
                }
            }
        }
    }
}
