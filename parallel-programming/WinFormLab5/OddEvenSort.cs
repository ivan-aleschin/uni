using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Lab5
{
    internal class OddEvenSort
    {
        public void Sort(int[,] matrix, int p)
        {
            int rowCount = matrix.GetLength(0);
            int chunk = rowCount / p;
            int remainder = rowCount % p;

            Parallel.For(0, p, i =>
            {
                int startRow = i * chunk + Math.Min(i, remainder);
                int endRow = startRow + chunk + (i < remainder ? 1 : 0);

                for (int row = startRow; row < endRow; row++)
                {
                    SortRow(matrix, row);
                }
            });
        }

        private void SortRow(int[,] matrix, int row)
        {
            int n = matrix.GetLength(1);
            bool sorted = false;

            while (!sorted)
            {
                sorted = true;

                for (int j = 0; j < n - 1; j += 2)
                {
                    if (matrix[row, j] > matrix[row, j + 1])
                    {
                        Swap(matrix, row, j, j + 1);
                        sorted = false;
                    }
                }

                for (int j = 1; j < n - 1; j += 2)
                {
                    if (matrix[row, j] > matrix[row, j + 1])
                    {
                        Swap(matrix, row, j, j + 1);
                        sorted = false;
                    }
                }
            }
        }

        private static void Swap(int[,] matrix, int row, int index1, int index2)
        {
            int temp = matrix[row, index1];
            matrix[row, index1] = matrix[row, index2];
            matrix[row, index2] = temp;
        }
    }
}
