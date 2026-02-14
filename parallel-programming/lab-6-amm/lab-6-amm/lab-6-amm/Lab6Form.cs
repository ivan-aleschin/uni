using System;
using System.Drawing;
using System.Windows.Forms;
using Lab6.AMM;
using Lab6.Algorithms;

namespace WinFormLab5
{
    public partial class Lab6Form : Form
    {
        private MatrixHoldem mh;
        private ParallelMatrixMachine<int> parallelMachine;
        private FloydWarshall<int> floydWarshall;

        public Lab6Form()
        {
            InitializeComponent();
            mh = new MatrixHoldem();
            parallelMachine = new ParallelMatrixMachine<int>();
            floydWarshall = new FloydWarshall<int>(parallelMachine);
        }

        private void btnGenerateGraph_Click(object sender, EventArgs e)
        {
            if (mh.InitializeRandomMatrixes(txtSize.Text, "4"))
            {
                // Преобразуем в матрицу смежности (0 и 1)
                ConvertToAdjacencyMatrix(mh.MatrixA);
                mh.Show(dataGridView1, mh.MatrixA);
            }
        }

        private void ConvertToAdjacencyMatrix(int[,] matrix)
        {
            int n = matrix.GetLength(0);
            Random rnd = new Random();
            
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i == j)
                        matrix[i, j] = 0;
                    else
                        matrix[i, j] = rnd.Next(2); // 0 или 1
                }
            }
        }

        private void btnTransitiveClosure_Click(object sender, EventArgs e)
        {
            if (mh.MatrixA != null)
            {
                var operation = new GraphTransitiveClosureOperation();
                var result = parallelMachine.Process(operation, mh.MatrixA);
                mh.Show(dataGridView2, result);
                lblResult.Text = "Транзитивное замыкание вычислено";
            }
        }

        private void btnShortestPaths_Click(object sender, EventArgs e)
        {
            if (mh.MatrixA != null)
            {
                // Создаем взвешенный граф
                CreateWeightedGraph(mh.MatrixA);
                var result = floydWarshall.FindShortestPaths(mh.MatrixA, int.MaxValue / 2);
                mh.Show(dataGridView2, result);
                lblResult.Text = "Кратчайшие пути найдены";
            }
        }

        private void btnConnectivity_Click(object sender, EventArgs e)
        {
            if (mh.MatrixA != null)
            {
                CreateWeightedGraph(mh.MatrixA);
                var result = floydWarshall.FindConnectivity(mh.MatrixA, int.MaxValue / 2);
                DisplayBoolMatrix(result, dataGridView2);
                lblResult.Text = "Матрица связности построена";
            }
        }

        private void CreateWeightedGraph(int[,] matrix)
        {
            int n = matrix.GetLength(0);
            Random rnd = new Random();
            
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i != j && matrix[i, j] == 1)
                    {
                        matrix[i, j] = rnd.Next(1, 10); // Веса от 1 до 9
                    }
                    else if (i == j)
                    {
                        matrix[i, j] = 0;
                    }
                    else
                    {
                        matrix[i, j] = int.MaxValue / 2; // "Бесконечность"
                    }
                }
            }
        }

        private void DisplayBoolMatrix(bool[,] matrix, DataGridView dgv)
        {
            int displaySize = Math.Min(20, matrix.GetLength(0));
            dgv.RowCount = displaySize;
            dgv.ColumnCount = displaySize;

            for (int i = 0; i < displaySize; i++)
            {
                dgv.Columns[i].Width = 30;
                for (int j = 0; j < displaySize; j++)
                {
                    dgv.Rows[i].Cells[j].Value = matrix[i, j] ? "1" : "0";
                    dgv.Rows[i].Cells[j].Style.BackColor = matrix[i, j] ? Color.LightGreen : Color.LightCoral;
                }
            }
        }
    }
}