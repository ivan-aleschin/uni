using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SAWA
{
    public partial class SAWAF : Form
    {
        SAWAC ssp = new SAWAC();
        public SAWAF()
        {
            InitializeComponent();
            tbB.Text = "10";
            tbN.Text = "6";
            tb_p.Text = "3";
        }

        private void btnCreate_Click(object sender, EventArgs e)
        {
            ssp.Init(tbN.Text, tbB.Text, tb_p.Text);
        }

        private void btnShowAB_Click(object sender, EventArgs e)
        {
            ssp.Show(dgArrs, false);
        }

        private void btnShowC_Click(object sender, EventArgs e)
        {
            ssp.Show(dgArrs, true);
        }

        private void btnSeq_Click(object sender, EventArgs e)
        {
            lblTime.Text = ssp.SeqSum();
        }

        private void btnPar_Click(object sender, EventArgs e)
        {
            lblTime.Text = ssp.ParSum();
        }

        private void dgArrs_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            lblTime.Text = ssp.PFSum();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            lblTime.Text = ssp.AVXSum();
        }
    }
}
