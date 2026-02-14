using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Lab5
{
    internal class CannonMethod
    {
        private int N, p;

        public CannonMethod(int N, int p) 
        {
            this.N = N; this.p = p;
        }

        private MatrixBlock[,] blocksA, blocksB, blocksC;
        public class MatrixBlock
        {
            public int[,] Data { get; set; }
            public int Size { get; set; }

            public MatrixBlock(int size)
            {
                Size = size;
                Data = new int[size, size];
            }
        }

        private MatrixBlock ExtractBlock(int[,] matrix, int blockRowStart, int blockColStart, int blockSize)
        {
            MatrixBlock block = new MatrixBlock(blockSize);

            int startRow = blockRowStart * blockSize;
            int startCol = blockColStart * blockSize;

            for (int i = 0; i < blockSize; ++i)
                for (int j = 0; j < blockSize; ++j)
                {
                    block.Data[i, j] = matrix[startRow + i, startCol + j];
                }
            return block;
        }

        private void InitializeBlocks(int[,] matrixA, int[,] matrixB, int blockSize)
        {
            blocksA = new MatrixBlock[p, p];
            blocksB = new MatrixBlock[p, p];
            blocksC = new MatrixBlock[p, p];

            for (int i = 0; i < p; i++)
                for (int j = 0; j < p; j++)
                {
                    blocksA[i, j] = ExtractBlock(matrixA, i, j, blockSize);
                    blocksB[i, j] = ExtractBlock(matrixB, i, j, blockSize);
                    blocksC[i, j] = new MatrixBlock(blockSize);
                }
        }

        private void InitialBlockSkew()
        {
            for (int i = 0; i < p; i++)
                for (int shift = 0; shift < i; shift++)
                {
                    ShiftRowBlocksLeft(blocksA, i);
                }

            for (int j = 0; j < p; j++)
                for (int shift = 0; shift < j; shift++)
                {
                    ShiftColumnBlocksUp(blocksB, j);
                }
        }

        private void ShiftRowBlocksLeft(MatrixBlock[,] blocks, int row)
        {
            MatrixBlock temp = blocks[row, 0];
            for (int j = 0; j < p - 1; j++)
            {
                blocks[row, j] = blocks[row, j + 1];
            }
            blocks[row, p - 1] = temp;
        }

        private void ShiftColumnBlocksUp(MatrixBlock[,] blocks, int col)
        {
            MatrixBlock temp = blocks[0, col];
            for (int i = 0; i < p - 1; i++)
            {
                blocks[i, col] = blocks[i + 1, col];
            }
            blocks[p - 1, col] = temp;
        }

        public string Multiply(int[,] matrixA, int[,] matrixB, int[,] result)
        {
            Stopwatch stopwatch = new Stopwatch();

            int blockSize = N / p;

            InitializeBlocks(matrixA, matrixB, blockSize);
            InitialBlockSkew();

            stopwatch.Start();
            for (int k = 0; k < p; k++)
            {
                MultiplyCurrentBlocks();

                if (k < p - 1)
                {
                    for (int j = 0; j < p; j++)
                    {
                        ShiftRowBlocksLeft(blocksA, j);
                    }
                    for (int j = 0; j < p; j++)
                    {
                        ShiftColumnBlocksUp(blocksB, j);
                    }
                }
            }
            stopwatch.Stop();

            AssembleResult(result);

            return stopwatch.Elapsed.ToString();
        }

        private void MultiplyCurrentBlocks()
        {
            Parallel.For(0, p, i =>
            {
                for (int j = 0; j < p; j++)
                {
                    MultiplyAndAddBlocks(blocksA[i, j], blocksB[i, j], blocksC[i, j]);
                }
            });
        }

        private void MultiplyAndAddBlocks(MatrixBlock blockA, MatrixBlock blockB, MatrixBlock blockC)
        {
            int blockSize = blockA.Size;

            for (int i = 0; i < blockSize; i++)
                for (int k = 0; k < blockSize; k++)
                    for (int j = 0; j < blockSize; j++)
                    {
                        blockC.Data[i, j] += blockA.Data[i, k] * blockB.Data[k, j];
                    }
        }

        private void CopyBlockToMatrix(MatrixBlock block, int[,] matrix, int startRow, int startCol)
        {
            for (int i = 0; i < block.Size; i++)
                for (int j = 0; j < block.Size; j++)
                {
                    matrix[startRow + i, startCol + j] = block.Data[i, j];
                }
        }

        private void AssembleResult(int[,] result)
        {
            int blockSize = N / p;

            for (int i = 0; i < p; i++)
                for (int j = 0; j < p; j++)
                {
                    CopyBlockToMatrix(blocksC[i, j], result, i * blockSize, j * blockSize);
                }
        }
    }
}
