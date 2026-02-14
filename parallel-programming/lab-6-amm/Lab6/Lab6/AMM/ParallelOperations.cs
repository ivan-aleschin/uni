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
            return operation.Execute(matrixA, matrixB);
        }
    }
}