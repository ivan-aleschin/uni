using Lab5;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.TaskbarClock;

namespace WinFormLab5
{
    public partial class Lab5 : Form
    {
        MatrixHoldem mh;
        public Lab5()
        {
            InitializeComponent();
            mh = new MatrixHoldem();    
        }

        private void button1_Click(object sender, EventArgs e)
        {
            mh.Clear(mh.MatrixA);
            if (mh.InitializeRandomMatrixes(textBox1.Text, textBox2.Text))
            {
                OddEvenSort oddEvenSort = new OddEvenSort();
                oddEvenSort.Sort(mh.MatrixA, mh.PNum);
                mh.Show(dataGridView1, mh.MatrixA);
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            mh.Clear(mh.MatrixA);
            mh.Clear(mh.MatrixB);
            mh.Clear(mh.MatrixC);
            if (mh.InitializeRandomMatrixes(textBox1.Text, textBox2.Text))
            {
                CannonMethodAlternative cannonMethod = new CannonMethodAlternative(mh.MatrixSize, mh.PNum);
                label5.Text = cannonMethod.Multiply(mh.MatrixA, mh.MatrixB, mh.MatrixC);
                mh.Show(dataGridView1, mh.MatrixA);
                mh.Show(dataGridView2, mh.MatrixB);
                mh.Show(dataGridView3, mh.MatrixC);
            }
        }

        private void button3_Click(object sender, EventArgs e)
        {
            mh.Clear(mh.MatrixA);
            mh.Clear(mh.MatrixB);
            mh.Clear(mh.MatrixC);
            if (mh.InitializeRandomMatrixes(textBox1.Text, textBox2.Text))
            {
 
                TapeMethod tapeMethod = new TapeMethod(mh.MatrixSize, mh.MatrixSize);
                label6.Text = tapeMethod.Multiply(mh.MatrixA, mh.MatrixB, mh.MatrixC);
                mh.Show(dataGridView1, mh.MatrixA);
                mh.Show(dataGridView2, mh.MatrixB);
                mh.Show(dataGridView3, mh.MatrixC);
            }
        }
    }
}
