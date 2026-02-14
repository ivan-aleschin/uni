using System;
using System.Drawing;
using System.Windows.Forms;
using Lab6.AMM;
using Lab6.Algorithms;
using Lab6.Services;

namespace Lab6.Forms
{
    public partial class MainForm : Form
    {
        private MatrixService matrixService;
        private ParallelMatrixMachine<int> parallelMachine;
        private FloydWarshall<int> floydWarshall;
        private int[,] currentMatrix;

        public MainForm()
        {
            InitializeComponent();
            matrixService = new MatrixService();
            parallelMachine = new ParallelMatrixMachine<int>();
            floydWarshall = new FloydWarshall<int>(parallelMachine);
            
            // Установка значений по умолчанию
            txtMatrixSize.Text = "6";
            txtInfinityValue.Text = "9999";
        }

        private void btnGenerateGraph_Click(object sender, EventArgs e)
        {
            if (int.TryParse(txtMatrixSize.Text, out int size) && size > 0)
            {
                currentMatrix = matrixService.CreateRandomAdjacencyMatrix(size, 0.3);
                matrixService.DisplayMatrix(dataGridViewOriginal, currentMatrix, "Исходный граф");
                lblStatus.Text = $"Сгенерирован граф {size}x{size}";
            }
            else
            {
                MessageBox.Show("Введите корректный размер матрицы", "Ошибка", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnTransitiveClosure_Click(object sender, EventArgs e)
        {
            if (currentMatrix != null)
            {
                var operation = new GraphTransitiveClosureOperation();
                var result = parallelMachine.Process(operation, currentMatrix);
                matrixService.DisplayBoolMatrix(dataGridViewResult, ConvertToBoolMatrix(result), "Транзитивное замыкание");
                lblStatus.Text = "Транзитивное замыкание вычислено";
            }
            else
            {
                MessageBox.Show("Сначала сгенерируйте матрицу", "Ошибка", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private void btnShortestPaths_Click(object sender, EventArgs e)
        {
            if (currentMatrix != null && int.TryParse(txtInfinityValue.Text, out int infinity))
            {
                var weightedMatrix = matrixService.ConvertToWeightedMatrix(currentMatrix, infinity);
                var result = floydWarshall.FindShortestPaths(weightedMatrix, infinity);
                matrixService.DisplayMatrix(dataGridViewResult, result, "Кратчайшие пути");
                lblStatus.Text = "Кратчайшие пути найдены";
            }
            else
            {
                MessageBox.Show("Сначала сгенерируйте матрицу и проверьте значение бесконечности", "Ошибка", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private void btnConnectivity_Click(object sender, EventArgs e)
        {
            if (currentMatrix != null && int.TryParse(txtInfinityValue.Text, out int infinity))
            {
                var weightedMatrix = matrixService.ConvertToWeightedMatrix(currentMatrix, infinity);
                var result = floydWarshall.FindConnectivity(weightedMatrix, infinity);
                matrixService.DisplayBoolMatrix(dataGridViewResult, result, "Связность");
                lblStatus.Text = "Матрица связности построена";
            }
            else
            {
                MessageBox.Show("Сначала сгенерируйте матрицу", "Ошибка", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private void btnLongestPaths_Click(object sender, EventArgs e)
        {
            if (currentMatrix != null && int.TryParse(txtInfinityValue.Text, out int infinity))
            {
                var weightedMatrix = matrixService.ConvertToWeightedMatrix(currentMatrix, infinity);
                var result = floydWarshall.FindLongestPaths(weightedMatrix, infinity);
                matrixService.DisplayMatrix(dataGridViewResult, result, "Длиннейшие пути");
                lblStatus.Text = "Длиннейшие пути найдены";
            }
            else
            {
                MessageBox.Show("Сначала сгенерируйте матрицу", "Ошибка", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private bool[,] ConvertToBoolMatrix(int[,] matrix)
        {
            int n = matrix.GetLength(0);
            var result = new bool[n, n];
            
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    result[i, j] = matrix[i, j] > 0;
                }
            }
            return result;
        }
    }
}