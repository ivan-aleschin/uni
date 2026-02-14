using System.Data.SqlClient;

namespace LabAB
{
    internal static class DbConfig
    {
        // SQL Server 2025 - РѕСЃРЅРѕРІРЅРѕР№ РёРЅСЃС‚Р°РЅСЃ СЃ РѕС‚РєР»СЋС‡РµРЅРёРµРј С€РёС„СЂРѕРІР°РЅРёСЏ РґР»СЏ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё
        public const string ConnectionString =
            @"Server=localhost;Database=LabAB;Integrated Security=True;TrustServerCertificate=True;";

        // РђР»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Рµ РІР°СЂРёР°РЅС‚С‹:
        // LocalDB: @"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=LabAB;Integrated Security=True;TrustServerCertificate=True;"
        // SQL Express: @"Server=localhost\SQLEXPRESS;Database=LabAB;Integrated Security=True;TrustServerCertificate=True;"

        public static SqlConnection CreateConnection()
        {
            return new SqlConnection(ConnectionString);
        }
    }
}
