using System;
using System.Threading.Tasks;
using Lab6.AMM;

namespace Lab6.AMM
{
    public class GraphTransitiveClosureOperation : MatrixOperation<int>
    {
        public override string OperationName => "TransitiveClosure";

        public override int[,] Execute(int[,] adjacencyMatrix, int[,] matrixB = null)
        {
            int n = adjacencyMatrix.GetLength(0);
            var result = (int[,])adjacencyMatrix.Clone();

            for (int k = 0; k < n; k++)
            {
                Parallel.For(0, n, i =>
                {
                    for (int j = 0; j < n; j++)
                    {
                        result[i, j] = result[i, j] != 0 || (result[i, k] != 0 && result[k, j] != 0) ? 1 : 0;
                    }
                });
            }

            return result;
        }
    }

    public class GraphDistanceOperation : MatrixOperation<int>
    {
        private readonly int _infinity;

        public GraphDistanceOperation(int infinity = int.MaxValue / 2)
        {
            _infinity = infinity;
        }

        public override string OperationName => "GraphDistance";

        public override int[,] Execute(int[,] adjacencyMatrix, int[,] matrixB = null)
        {
            int n = adjacencyMatrix.GetLength(0);
            var distance = new int[n, n];

            // Инициализация матрицы расстояний
            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < n; j++)
                {
                    if (i == j)
                        distance[i, j] = 0;
                    else if (adjacencyMatrix[i, j] != 0)
                        distance[i, j] = adjacencyMatrix[i, j];
                    else
                        distance[i, j] = _infinity;
                }
            });

            // Алгоритм Флойда-Уоршелла
            for (int k = 0; k < n; k++)
            {
                Parallel.For(0, n, i =>
                {
                    for (int j = 0; j < n; j++)
                    {
                        if (distance[i, k] != _infinity && distance[k, j] != _infinity)
                        {
                            int throughK = distance[i, k] + distance[k, j];
                            if (throughK < distance[i, j])
                            {
                                distance[i, j] = throughK;
                            }
                        }
                    }
                });
            }

            return distance;
        }
    }
}