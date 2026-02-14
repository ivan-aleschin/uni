using System;
using System.Data;
using System.Windows.Forms;

namespace AMM
{
    /// <summary>
    /// Реализация работы с булевыми матрицами для формы.
    /// Использует абстрактную матричную машину AMMimp&lt;bool&gt;.
    /// </summary>
    class AMMRB
    {
        private int i, j, N;
        private bool[,] rA, rB, rC;

        private readonly AMMimp<bool> _boolMachine =
            new AMMimp<bool>(new BoolConnectivityOps());

        /// <summary>
        /// Инициализация булевых матриц случайными значениями и привязка к DataGridView.
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

                rA = new bool[N, N];
                rB = new bool[N, N];
                rC = new bool[N, N];

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
                        rA[i, j] = Convert.ToBoolean(rw.Next(2));
                        _A.Rows[i].Cells[j].Value = rA[i, j].ToString();

                        rB[i, j] = Convert.ToBoolean(rw.Next(2));
                        _B.Rows[i].Cells[j].Value = rB[i, j].ToString();
                    }

                return true;
            }
            else
                return false;
        }

        /// <summary>
        /// Булево "сложение" матриц C = A OR B (элементно).
        /// </summary>
        public void AddM()
        {
            if (rA == null || rB == null || rC == null) return;
            _boolMachine.AddMatrices(rA, rB, rC);
        }

        /// <summary>
        /// Булево "умножение" матриц C = A ⊗ B, где
        /// ⊕ = OR, ⊗ = AND (классический булев матричный продукт).
        /// </summary>
        public void MultM()
        {
            if (rA == null || rB == null || rC == null) return;
            _boolMachine.MultiplyMatrices(rA, rB, rC);
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

        #region Связность графа (транзитивное замыкание)

        /// <summary>
        /// Считаем rA матрицей смежности ориентированного графа (true = есть ребро).
        /// Строим транзитивное замыкание в rC (достижимость всех пар вершин)
        /// с помощью алгоритма Флойда-Уоршелла над булевым семирингом.
        /// </summary>
        public void ComputeConnectivityClosure()
        {
            if (rA == null) return;
            int n = N;

            // Копируем матрицу смежности в рабочую матрицу.
            bool[,] d = new bool[n, n];
            Array.Copy(rA, d, rA.Length);

            _boolMachine.FloydWarshall(d);
            rC = d;
        }

        public void UpdateAFromGrid(DataGridView grid)
        {
            if (grid == null)
                throw new ArgumentNullException(nameof(grid));

            int rows = grid.RowCount;
            int cols = grid.ColumnCount;
            if (rows == 0 || cols == 0)
                return;

            N = Math.Min(rows, cols);

            rA = new bool[N, N];
            if (rB == null || rB.GetLength(0) != N || rB.GetLength(1) != N)
                rB = new bool[N, N];
            if (rC == null || rC.GetLength(0) != N || rC.GetLength(1) != N)
                rC = new bool[N, N];

            for (int i = 0; i < N; i++)
            {
                for (int j = 0; j < N; j++)
                {
                    object cellValue = grid.Rows[i].Cells[j].Value;
                    bool value = false;
                    if (cellValue != null)
                        Boolean.TryParse(cellValue.ToString(), out value);
                    rA[i, j] = value;
                }
            }
        }


        public void UpdateABFromGrids(DataGridView gridA, DataGridView gridB)
        {
            if (gridA == null) throw new ArgumentNullException(nameof(gridA));
            if (gridB == null) throw new ArgumentNullException(nameof(gridB));

            int rowsA = gridA.RowCount;
            int colsA = gridA.ColumnCount;
            int rowsB = gridB.RowCount;
            int colsB = gridB.ColumnCount;

            if (rowsA == 0 || colsA == 0 || rowsB == 0 || colsB == 0)
                return;

            // Берём минимальный размер, чтобы точно не выйти за границы
            N = Math.Min(Math.Min(rowsA, colsA), Math.Min(rowsB, colsB));

            rA = new bool[N, N];
            rB = new bool[N, N];
            if (rC == null || rC.GetLength(0) != N || rC.GetLength(1) != N)
                rC = new bool[N, N];

            for (int i = 0; i < N; i++)
            {
                for (int j = 0; j < N; j++)
                {
                    // читаем A
                    bool valA = false;
                    object cellA = gridA.Rows[i].Cells[j].Value;
                    if (cellA != null)
                        Boolean.TryParse(cellA.ToString(), out valA);
                    rA[i, j] = valA;

                    // читаем B
                    bool valB = false;
                    object cellB = gridB.Rows[i].Cells[j].Value;
                    if (cellB != null)
                        Boolean.TryParse(cellB.ToString(), out valB);
                    rB[i, j] = valB;
                }
            }
        }


        #endregion
    }
}
