using System;
using System.Diagnostics;
using System.Threading.Tasks;

namespace Lab5
{
    internal class CannonMethodAlternative
    {
        private int N, p;

        public CannonMethodAlternative(int N, int p)
        {
            this.N = N; this.p = p;
        }

        public string Multiply(int[,] matrixA, int[,] matrixB, int[,] result)
        {
            int blockSize = N / p;

            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();

            for (int k = 0; k < p; k++)
            {
                Parallel.For(0, p, i =>
                {
                    for (int j = 0; j < p; j++)
                    {
                        int aCol = (j + i + k) % p;
                        int bRow = (i + j + k) % p;

                        for (int bi = 0; bi < blockSize; bi++)
                        {
                            int aRowGlobal = i * blockSize + bi;
                            for (int bj = 0; bj < blockSize; bj++)
                            {
                                int bColGlobal = j * blockSize + bj;
                                int sum = 0;
                                for (int bk = 0; bk < blockSize; bk++)
                                {
                                    int aColGlobal = aCol * blockSize + bk;
                                    int bRowGlobal = bRow * blockSize + bk;
                                    sum += matrixA[aRowGlobal, aColGlobal] * matrixB[bRowGlobal, bColGlobal];
                                }
                                result[aRowGlobal, bColGlobal] += sum;
                            }
                        }
                    }
                });
            }

            stopwatch.Stop();
            return stopwatch.Elapsed.ToString();
        }
    }
}