using System.Threading.Tasks;

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
                        if (result[i, j] == 0)
                        {
                            result[i, j] = (result[i, k] != 0 && result[k, j] != 0) ? 1 : 0;
                        }
                    }
                });
            }

            return result;
        }
    }
}