using System;
using System.Drawing;
using System.Windows.Forms;

namespace Lab6.Services
{
    public class MatrixService
    {
        public int[,] CreateRandomMatrix(int size, int minValue = 0, int maxValue = 10)
        {
            var matrix = new int[size, size];
            Random rnd = new Random();
            
            for (int i = 0; i < size; i++)
            {
                for (int j = 0; j < size; j++)
                {
                    matrix[i, j] = rnd.Next(minValue, maxValue);
                }
            }
            return matrix;
        }

        public int[,] CreateRandomAdjacencyMatrix(int size, double density = 0.3)
        {
            var matrix = new int[size, size];
            Random rnd = new Random();
            
            for (int i = 0; i < size; i++)
            {
                for (int j = 0; j < size; j++)
                {
                    if (i == j)
                        matrix[i, j] = 0;
                    else
                        matrix[i, j] = rnd.NextDouble() < density ? rnd.Next(1, 10) : int.MaxValue / 2;
                }
            }
            return matrix;
        }

        public void DisplayMatrix(DataGridView dataGridView, int[,] matrix, string title = "")
        {
            if (matrix == null) return;

            int displaySize = Math.Min(20, matrix.GetLength(0));
            
            dataGridView.Rows.Clear();
            dataGridView.Columns.Clear();

            // Создаем колонки
            for (int i = 0; i < displaySize; i++)
            {
                dataGridView.Columns.Add($"Col{i}", $"{i}");
                dataGridView.Columns[i].Width = 40;
            }

            // Заполняем данными
            for (int i = 0; i < displaySize; i++)
            {
                dataGridView.Rows.Add();
                for (int j = 0; j < displaySize; j++)
                {
                    if (matrix[i, j] == int.MaxValue / 2)
                        dataGridView.Rows[i].Cells[j].Value = "∞";
                    else
                        dataGridView.Rows[i].Cells[j].Value = matrix[i, j].ToString();
                }
            }

            if (!string.IsNullOrEmpty(title))
                dataGridView.Columns[0].HeaderText = title;
        }

        public void DisplayBoolMatrix(DataGridView dataGridView, bool[,] matrix, string title = "")
        {
            if (matrix == null) return;

            int displaySize = Math.Min(20, matrix.GetLength(0));
            
            dataGridView.Rows.Clear();
            dataGridView.Columns.Clear();

            for (int i = 0; i < displaySize; i++)
            {
                dataGridView.Columns.Add($"Col{i}", $"{i}");
                dataGridView.Columns[i].Width = 30;
            }

            for (int i = 0; i < displaySize; i++)
            {
                dataGridView.Rows.Add();
                for (int j = 0; j < displaySize; j++)
                {
                    dataGridView.Rows[i].Cells[j].Value = matrix[i, j] ? "1" : "0";
                    dataGridView.Rows[i].Cells[j].Style.BackColor = matrix[i, j] ? Color.LightGreen : Color.LightCoral;
                }
            }

            if (!string.IsNullOrEmpty(title))
                dataGridView.Columns[0].HeaderText = title;
        }
    }
}