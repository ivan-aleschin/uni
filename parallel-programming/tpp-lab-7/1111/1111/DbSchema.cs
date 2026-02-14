using System.Data.SqlClient;

namespace LabAB
{
    internal static class DbSchema
    {
        // Р”Р»РёРЅР° РєР»СЋС‡Р° NCHAR(L)
        public const int KeyLength = 10;

        /// <summary>
        /// РЎРѕР·РґР°С‘С‚ Р±Р°Р·Сѓ РґР°РЅРЅС‹С… LabAB, РµСЃР»Рё РѕРЅР° РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚
        /// </summary>
        public static void EnsureDatabaseExists()
        {
            // РџРѕРґРєР»СЋС‡Р°РµРјСЃСЏ Рє СЃРёСЃС‚РµРјРЅРѕР№ Р‘Р” master РґР»СЏ СЃРѕР·РґР°РЅРёСЏ LabAB
            string masterConnectionString = DbConfig.ConnectionString.Replace("Database=LabAB", "Database=master");
            
            using (var con = new SqlConnection(masterConnectionString))
            {
                con.Open();
                
                string checkDbSql = @"
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'LabAB')
BEGIN
    CREATE DATABASE LabAB;
END";
                using (var cmd = new SqlCommand(checkDbSql, con))
                {
                    cmd.ExecuteNonQuery();
                }
            }
        }

        /// <summary>
        /// РџРµСЂРµСЃРѕР·РґР°С‘С‚ С„РёР·РёС‡РµСЃРєРёРµ С‚Р°Р±Р»РёС†С‹ A, B Рё СѓРґР°Р»СЏРµС‚ РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Рµ.
        /// РСЃРїРѕР»СЊР·СѓРµРј РїРѕР»Рµ A СЃ NCHAR(L) РїРѕРґ PK/INDEX.
        /// </summary>
        public static void RecreateTables()
        {
            // РЎРЅР°С‡Р°Р»Р° СѓР±РµР¶РґР°РµРјСЃСЏ, С‡С‚Рѕ Р±Р°Р·Р° РґР°РЅРЅС‹С… СЃСѓС‰РµСЃС‚РІСѓРµС‚
            EnsureDatabaseExists();
            
            using (var con = DbConfig.CreateConnection())
            {
                con.Open();

                string sql = $@"
IF OBJECT_ID('dbo.Asrt', 'U') IS NOT NULL DROP TABLE dbo.Asrt;
IF OBJECT_ID('dbo.Bsrt', 'U') IS NOT NULL DROP TABLE dbo.Bsrt;
IF OBJECT_ID('dbo.AjB_sql', 'U') IS NOT NULL DROP TABLE dbo.AjB_sql;
IF OBJECT_ID('dbo.AjB_merge', 'U') IS NOT NULL DROP TABLE dbo.AjB_merge;

IF OBJECT_ID('dbo.A', 'U') IS NOT NULL DROP TABLE dbo.A;
IF OBJECT_ID('dbo.B', 'U') IS NOT NULL DROP TABLE dbo.B;

CREATE TABLE dbo.A
(
    A  NCHAR({KeyLength}) NOT NULL,
    B  INT                NOT NULL,
    D1 INT                NULL,
    D2 FLOAT              NULL
);

CREATE TABLE dbo.B
(
    A  NCHAR({KeyLength}) NOT NULL,
    C  INT                NOT NULL,
    E1 INT                NULL,
    E2 FLOAT              NULL
);
";
                using (var cmd = new SqlCommand(sql, con))
                {
                    cmd.ExecuteNonQuery();
                }
            }
        }
    }
}
