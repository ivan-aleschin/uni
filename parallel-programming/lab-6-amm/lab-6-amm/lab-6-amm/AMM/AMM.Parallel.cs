using System;
using System.Threading.Tasks;

namespace Lab6.AMM
{
    public class ParallelMatrixMachine<T> : MatrixMachine<T>
    {
        private readonly int _degreeOfParallelism;

        public ParallelMatrixMachine(int degreeOfParallelism = -1)
        {
            _degreeOfParallelism = degreeOfParallelism;
        }

        public override string MachineType => "ParallelMatrixMachine";

        public override T[,] Process(MatrixOperation<T> operation, T[,] matrixA, T[,] matrixB = null)
        {
            Console.WriteLine($"Executing {operation.OperationName} on {MachineType}");
            return operation.Execute(matrixA, matrixB);
        }
    }

    // Базовые параллельные операции
    public class ParallelAddOperation<T> : MatrixOperation<T> where T : struct
    {
        public override T[,] Execute(T[,] matrixA, T[,] matrixB = null)
        {
            int rows = matrixA.GetLength(0);
            int cols = matrixA.GetLength(1);
            var result = new T[rows, cols];

            Parallel.For(0, rows, i =>
            {
                for (int j = 0; j < cols; j++)
                {
                    dynamic a = matrixA[i, j];
                    dynamic b = matrixB[i, j];
                    result[i, j] = a + b;
                }
            });

            return result;
        }
    }

    public class ParallelMultiplyOperation<T> : MatrixOperation<T> where T : struct
    {
        public override T[,] Execute(T[,] matrixA, T[,] matrixB = null)
        {
            int n = matrixA.GetLength(0);
            var result = new T[n, n];

            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < n; j++)
                {
                    dynamic sum = default(T);
                    for (int k = 0; k < n; k++)
                    {
                        dynamic a = matrixA[i, k];
                        dynamic b = matrixB[k, j];
                        sum += a * b;
                    }
                    result[i, j] = sum;
                }
            });

            return result;
        }
    }
}