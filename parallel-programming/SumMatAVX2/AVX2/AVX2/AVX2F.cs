using AVX2Mat;
using System;
using System.Windows.Forms;

namespace AVX2
{
    public partial class AVX2F : Form
    {
        AVX2C sumArr = new AVX2C();
        AVX2MatDisp sumMats = new AVX2MatDisp();
        int i;
        public AVX2F()
        {
            InitializeComponent();
            dgA.RowCount = 8;
            dgB.RowCount = 8;
            dgC.RowCount = 8;
            dgA.ColumnCount = 8;
            dgB.ColumnCount = 8;
            dgC.ColumnCount = 8;

            for (i = 0; i < 8; i++)
            {
                dgA.Columns[i].Width = dgA.Width / 9;
                dgB.Columns[i].Width = dgB.Width / 9;
                dgC.Columns[i].Width = dgC.Width / 9;
            }
        }

        private void btnStart_Click(object sender, System.EventArgs e)
        {
            sumArr.GenArr(tbN.Text);
        }

        private void btnStartMat_Click(object sender, System.EventArgs e)
        {
            sumMats.GenAndSum(tbN.Text, tb_p.Text);
        }

        private void btnShowMat_Click(object sender, EventArgs e)
        {
            sumMats.ShowMatrices(dgA, dgB, dgC);
        }
    }
}
