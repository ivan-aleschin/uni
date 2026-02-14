using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WinFormLab5
{
    internal class MatrixHoldem
    {
        int N, p;
        int[,] matrixA, matrixB, matrixC;
        public int[,] MatrixA => matrixA;
        public int[,] MatrixB => matrixB;
        public int[,] MatrixC => matrixC;
        public int MatrixSize => N;
        public int PNum => p;

        public bool InitializeRandomMatrixes(string _N, string _P)
        {
            if (Int32.TryParse(_N, out N) && Int32.TryParse(_P, out p) && N > 0 && p > 0)
            {
                matrixA = new int[N, N];
                matrixB = new int[N, N];
                matrixC = new int[N, N];
                Random rw = new Random();

                for (int i = 0; i < N; ++i)
                    for (int j = 0; j < N; ++j)
                    {
                        matrixA[i, j] = rw.Next(3);
                        matrixB[i, j] = rw.Next(3);
                    }
                return true;
            }
            else
                return false;
        }

        public void Clear(int[,] matx)
        {
            for (int i = 0; i < N; ++i)
                for (int j = 0; j < N; ++j)
                    matx[i, j] = 0;
        }

        public void Show(DataGridView dgv, int[,] matrix)
        {
            if (matrix == null) return;

            int displaySize = Math.Min(20, N);
            dgv.RowCount = displaySize;
            dgv.ColumnCount = displaySize;

            for (int i = 0; i < displaySize; ++i)
            {
                dgv.Columns[i].Width = 40;
                for (int j = 0; j < displaySize; ++j)
                {
                    dgv.Rows[i].Cells[j].Value = matrix[i, j].ToString();
                }
            }
        }

    }
}
