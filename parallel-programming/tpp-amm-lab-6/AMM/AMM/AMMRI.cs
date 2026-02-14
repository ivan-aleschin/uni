using System;
using System.Data;
using System.Windows.Forms;

namespace AMM
{
    /// <summary>
    /// Реализация работы с целочисленными матрицами для формы.
    /// Использует абстрактную матричную машину AMMimp&lt;int&gt;.
    /// </summary>
    class AMMRI
    {
        private int i, j, N;
        private int[,] rA, rB, rC;

        // Машина для обычного сложения/умножения матриц (арифметика int).
        private readonly AMMimp<int> _arithMachine =
            new AMMimp<int>(new IntArithmeticOps());

        // Машины для задач графов (Флойд-Уоршелл).
        private readonly int _inf = int.MaxValue / 2;
        private readonly int _negInf = int.MinValue / 2;

        private readonly AMMimp<int> _shortestMachine;
        private readonly AMMimp<int> _longestMachine;

        public AMMRI()
        {
            _shortestMachine = new AMMimp<int>(new IntShortestPathOps(_inf));
            _longestMachine = new AMMimp<int>(new IntLongestPathOps(_negInf));
        }

        /// <summary>
        /// Инициализация матриц случайными числами (0..2) и привязка к DataGridView.
        /// </summary>
        public bool InitRnd(string _N, DataGridView _A, DataGridView _B, DataGridView _C)
        {
            if (Int32.TryParse(_N, out N))
            {
                _A.RowCount = N;
                _B.RowCount = N;
                _C.RowCount = N;
                _A.ColumnCount = N;
                _B.ColumnCount = N;
                _C.ColumnCount = N;

                rA = new int[N, N];
                rB = new int[N, N];
                rC = new int[N, N];

                Random rw = new Random();

                for (i = 0; i < N; i++)
                {
                    _A.Columns[i].Width = _A.Width / (N + 1);
                    _B.Columns[i].Width = _B.Width / (N + 1);
                    _C.Columns[i].Width = _C.Width / (N + 1);
                }

                for (i = 0; i < N; i++)
                    for (j = 0; j < N; j++)
                    {
                        rA[i, j] = rw.Next(3);
                        _A.Rows[i].Cells[j].Value = rA[i, j].ToString();

                        rB[i, j] = rw.Next(3);
                        _B.Rows[i].Cells[j].Value = rB[i, j].ToString();
                    }

                return true;
            }
            else
                return false;
        }

        /// <summary>
        /// Матричное сложение C = A + B с использованием параллельной АММ.
        /// </summary>
        public void AddM()
        {
            if (rA == null || rB == null || rC == null) return;
            _arithMachine.AddMatrices(rA, rB, rC);
        }

        /// <summary>
        /// Матричное умножение C = A * B с использованием параллельной АММ.
        /// </summary>
        public void MultM()
        {
            if (rA == null || rB == null || rC == null) return;
            _arithMachine.MultiplyMatrices(rA, rB, rC);
        }

        /// <summary>
        /// Показать матрицу результата в DataGridView.
        /// </summary>
        public void Show(DataGridView _C)
        {
            if (rC == null) return;

            for (i = 0; i < N; i++)
                for (j = 0; j < N; j++)
                {
                    _C.Rows[i].Cells[j].Value = rC[i, j].ToString();
                }
        }

        #region Алгоритм Флойда-Уоршелла для графов на int-матрицах

        /// <summary>
        /// Считаем rA матрицей весов графа.
        /// Строим матрицу всех кратчайших путей в rC (Флойд-Уоршелл, min/+).
        /// 0 на диагонали, 0 вне диагонали трактуется как «нет ребра».
        /// </summary>
        public void ComputeAllPairsShortestPaths()
        {
            if (rA == null) return;

            int n = N;
            int[,] d = new int[n, n];

            // Инициализация матрицы расстояний.
            for (int u = 0; u < n; u++)
            {
                for (int v = 0; v < n; v++)
                {
                    if (u == v)
                        d[u, v] = 0;
                    else if (rA[u, v] != 0)
                        d[u, v] = rA[u, v];
                    else
                        d[u, v] = _inf;
                }
            }

            _shortestMachine.FloydWarshall(d);
            rC = d;
        }

        /// <summary>
        /// Считаем rA матрицей весов графа.
        /// Строим матрицу всех длиннейших путей в rC (Флойд-Уоршелл, max/+).
        /// 0 на диагонали, 0 вне диагонали трактуется как «нет ребра».
        /// </summary>
        public void ComputeAllPairsLongestPaths()
        {
            if (rA == null) return;

            int n = N;
            int[,] d = new int[n, n];

            // Инициализация матрицы расстояний.
            for (int u = 0; u < n; u++)
            {
                for (int v = 0; v < n; v++)
                {
                    if (u == v)
                        d[u, v] = 0;
                    else if (rA[u, v] != 0)
                        d[u, v] = rA[u, v];
                    else
                        d[u, v] = _negInf;
                }
            }

            _longestMachine.FloydWarshall(d);
            rC = d;
        }

        /// <summary>
        /// Вернуть кратчайший путь от вершины from до вершины to
        /// как последовательность индексов вершин.
        /// rA трактуется как матрица весов; 0 вне диагонали — нет ребра.
        /// </summary>
        public int[] GetShortestPath(int from, int to)
        {
            if (rA == null) return null;
            int n = N;
            if (from < 0 || from >= n || to < 0 || to >= n)
                return null;

            int[,] d = new int[n, n];
            int?[,] next = new int?[n, n];

            // Инициализация матрицы расстояний и матрицы разузлования.
            for (int u = 0; u < n; u++)
            {
                for (int v = 0; v < n; v++)
                {
                    if (u == v)
                    {
                        d[u, v] = 0;
                        next[u, v] = v;
                    }
                    else if (rA[u, v] != 0)
                    {
                        d[u, v] = rA[u, v];
                        next[u, v] = v;
                    }
                    else
                    {
                        d[u, v] = _inf;
                        next[u, v] = null;
                    }
                }
            }

            _shortestMachine.FloydWarshallWithPath(d, next);
            return AMMimp<int>.ReconstructPath(from, to, next);
        }

        public void UpdateAFromGrid(DataGridView grid)
        {
            if (grid == null)
                throw new ArgumentNullException(nameof(grid));

            int rows = grid.RowCount;
            int cols = grid.ColumnCount;
            if (rows == 0 || cols == 0)
                return;

            // считаем, что матрица квадратная: N = min(rows, cols)
            N = Math.Min(rows, cols);

            // пересоздаём rA (и при необходимости rB, rC) под этот размер
            rA = new int[N, N];
            if (rB == null || rB.GetLength(0) != N || rB.GetLength(1) != N)
                rB = new int[N, N];
            if (rC == null || rC.GetLength(0) != N || rC.GetLength(1) != N)
                rC = new int[N, N];

            for (int i = 0; i < N; i++)
            {
                for (int j = 0; j < N; j++)
                {
                    object cellValue = grid.Rows[i].Cells[j].Value;
                    int value;
                    if (cellValue == null || !int.TryParse(cellValue.ToString(), out value))
                        value = 0;
                    rA[i, j] = value;
                }
            }
        }


        #endregion
    }
}
