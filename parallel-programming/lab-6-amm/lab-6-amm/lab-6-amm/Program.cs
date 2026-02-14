using System;
using System.Windows.Forms;
using lab-6-amm.Forms;

namespace lab-6-amm
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}