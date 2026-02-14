using System;
using System.Threading.Tasks;

namespace Lab6.AMM
{
    public abstract class MatrixOperation<T>
    {
        public abstract T[,] Execute(T[,] matrixA, T[,] matrixB = null);
        public virtual string OperationName => GetType().Name;
    }

    public abstract class MatrixMachine<T>
    {
        public abstract T[,] Process(MatrixOperation<T> operation, T[,] matrixA, T[,] matrixB = null);
        public abstract string MachineType { get; }
    }
}