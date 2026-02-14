using System;
using System.Threading.Tasks;
using Lab6.AMM;

namespace Lab6.Algorithms
{
    public class FloydWarshall<T> where T : struct, IComparable<T>
    {
        private readonly MatrixMachine<T> _matrixMachine;

        public FloydWarshall(MatrixMachine<T> matrixMachine)
        {
            _matrixMachine = matrixMachine;
        }

        public T[,] FindShortestPaths(T[,] graph, T infinity)
        {
            int n = graph.GetLength(0);
            var dist = (T[,])graph.Clone();

            // Инициализация диагонали
            for (int i = 0; i < n; i++)
            {
                dist[i, i] = default(T);
            }

            var minOperation = new FloydMinOperation<T>(infinity);
            
            for (int k = 0; k < n; k++)
            {
                Parallel.For(0, n, i =>
                {
                    for (int j = 0; j < n; j++)
                    {
                        if (dist[i, k].CompareTo(infinity) < 0 && 
                            dist[k, j].CompareTo(infinity) < 0)
                        {
                            dynamic throughK = dist[i, k];
                            throughK += dist[k, j];
                            
                            if (throughK.CompareTo(dist[i, j]) < 0)
                            {
                                dist[i, j] = throughK;
                            }
                        }
                    }
                });
            }

            return dist;
        }

        public bool[,] FindConnectivity(T[,] graph, T infinity)
        {
            int n = graph.GetLength(0);
            var connectivity = new bool[n, n];

            var dist = FindShortestPaths(graph, infinity);

            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < n; j++)
                {
                    connectivity[i, j] = dist[i, j].CompareTo(infinity) < 0;
                }
            });

            return connectivity;
        }

        public T[,] FindLongestPaths(T[,] graph, T infinity)
        {
            // Для поиска длиннейших путей инвертируем веса
            int n = graph.GetLength(0);
            var invertedGraph = new T[n, n];
            
            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < n; j++)
                {
                    if (i == j)
                    {
                        invertedGraph[i, j] = default(T);
                    }
                    else if (graph[i, j].CompareTo(infinity) == 0)
                    {
                        invertedGraph[i, j] = infinity;
                    }
                    else
                    {
                        dynamic weight = graph[i, j];
                        invertedGraph[i, j] = -weight;
                    }
                }
            });

            var result = FindShortestPaths(invertedGraph, infinity);
            
            // Инвертируем обратно
            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < n; j++)
                {
                    if (result[i, j].CompareTo(infinity) < 0)
                    {
                        dynamic weight = result[i, j];
                        result[i, j] = -weight;
                    }
                }
            });

            return result;
        }
    }

    internal class FloydMinOperation<T> : MatrixOperation<T> where T : IComparable<T>
    {
        private readonly T _infinity;

        public FloydMinOperation(T infinity)
        {
            _infinity = infinity;
        }

        public override T[,] Execute(T[,] matrixA, T[,] matrixB = null)
        {
            throw new NotImplementedException("This operation is used internally in Floyd-Warshall");
        }
    }
}