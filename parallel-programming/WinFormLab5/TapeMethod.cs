using System;
using System.Diagnostics;
using System.Threading.Tasks;

namespace Lab5
{
    internal class TapeMethod
    {
        private int N, p;
        private int[][][] processDataA;
        private int[][][] processDataB;
        private int[][][] processResultsC;

        public TapeMethod(int N, int p)
        {
            this.N = N; 
            this.p = p;
        }
        
        private void InitializeProcessData(int[,] matrixA, int[,] matrixB)
        {
            processDataA = new int[p][][];
            processDataB = new int[p][][];
            processResultsC = new int[p][][];

            int blockSize = N / p;
            
            for (int i = 0; i < p; i++)
            {
                processDataA[i] = new int[blockSize][];
                processDataB[i] = new int[blockSize][];
                processResultsC[i] = new int[blockSize][];
                
                for (int j = 0; j < blockSize; j++)
                {
                    processDataA[i][j] = new int[N];
                    processDataB[i][j] = new int[N];
                    processResultsC[i][j] = new int[N];
                    
                    // Копируем блок строки матрицы A
                    for (int k = 0; k < N; k++)
                    {
                        processDataA[i][j][k] = matrixA[i * blockSize + j, k];
                    }
                    
                    // Копируем блок столбца матрицы B
                    for (int k = 0; k < N; k++)
                    {
                        processDataB[i][j][k] = matrixB[k, i * blockSize + j];
                    }
                }
            }
        }

        public string Multiply(int[,] matrixA, int[,] matrixB, int[,] result)
        {
            if (N % p != 0)
            {
                throw new ArgumentException("N must be divisible by p");
            }

            Stopwatch stopwatch = new Stopwatch();
            InitializeProcessData(matrixA, matrixB);

            stopwatch.Start();
            
            for (int iter = 0; iter < p; iter++)
            {
                Parallel.For(0, p, i =>
                {
                    int blockSize = N / p;
                    int partnerA = (i + iter) % p;
                    int partnerB = i; // B не сдвигается между процессами

                    for (int row = 0; row < blockSize; row++)
                    {
                        for (int col = 0; col < N; col++)
                        {
                            int sum = 0;
                            for (int k = 0; k < blockSize; k++)
                            {
                                // Умножаем строку из A на столбец из B
                                sum += processDataA[partnerA][row][k + i * blockSize] * 
                                       processDataB[partnerB][k][col];
                            }
                            processResultsC[i][row][col] += sum;
                        }
                    }
                });
            }
            
            stopwatch.Stop();
            AssembleResult(result);
            return stopwatch.Elapsed.ToString();
        }

        private void AssembleResult(int[,] result)
        {
            int blockSize = N / p;
            for (int i = 0; i < p; i++)
            {
                for (int row = 0; row < blockSize; row++)
                {
                    for (int col = 0; col < N; col++)
                    {
                        result[i * blockSize + row, col] = processResultsC[i][row][col];
                    }
                }
            }
        }
    }
}