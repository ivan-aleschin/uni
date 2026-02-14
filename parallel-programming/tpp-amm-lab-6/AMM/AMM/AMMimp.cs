using System;
using System.Threading.Tasks;

namespace AMM
{
    /// <summary>
    /// Абстракция операций над элементами матрицы (семиринг).
    /// За счёт этого одна и та же матричная машина может работать
    /// с целыми числами, булевыми значениями, длинами путей и т.д.
    /// </summary>
    public abstract class AmmOps<T>
    {
        /// Нейтральный элемент для "сложения"
        public abstract T Zero { get; }

        /// Нейтральный элемент для "умножения" (⊗)
        public abstract T One { get; }

        ///"Сложение" (⊕) в абстрактном смысле
        public abstract T Add(T a, T b);

        /// "Умножение" (⊗) в абстрактном смысле
        public abstract T Mul(T a, T b);

        /// <summary>
        /// Критерий «лучше», используемый в алгоритмах типа Флойда-Уоршелла.
        /// Должен возвращать true, если candidate "лучше" текущего значения current.
        /// </summary>
        public abstract bool Better(T candidate, T current);
    }

    /// <summary>
    /// Абстрактная матричная машина.
    /// Реализует параллельные операции над матрицами: сложение, умножение
    /// и алгоритм Флойда-Уоршелла (в том числе с разузлованием пути).
    /// </summary>
    public class AMMimp<T>
    {
        private readonly AmmOps<T> _ops;

        public AMMimp(AmmOps<T> ops)
        {
            _ops = ops ?? throw new ArgumentNullException(nameof(ops));
        }

        /// <summary>
        /// Параллельное по строкам сложение матриц C = A ⊕ B.
        /// Размеры матриц должны совпадать.
        /// </summary>
        public void AddMatrices(T[,] A, T[,] B, T[,] C)
        {
            if (A == null) throw new ArgumentNullException(nameof(A));
            if (B == null) throw new ArgumentNullException(nameof(B));
            if (C == null) throw new ArgumentNullException(nameof(C));

            int n = A.GetLength(0);
            int m = A.GetLength(1);

            if (B.GetLength(0) != n || B.GetLength(1) != m ||
                C.GetLength(0) != n || C.GetLength(1) != m)
                throw new ArgumentException("Размеры матриц A, B и C должны совпадать.");

            Parallel.For(0, n, i =>
            {
                for (int j = 0; j < m; j++)
                {
                    C[i, j] = _ops.Add(A[i, j], B[i, j]);
                }
            });
        }

        /// <summary>
        /// Параллельное по строкам умножение матриц C = A ⊗ B
        /// (используются операции Add/Mul из AmmOps).
        /// </summary>
        public void MultiplyMatrices(T[,] A, T[,] B, T[,] C)
        {
            if (A == null) throw new ArgumentNullException(nameof(A));
            if (B == null) throw new ArgumentNullException(nameof(B));
            if (C == null) throw new ArgumentNullException(nameof(C));

            int n = A.GetLength(0);
            int m = A.GetLength(1);
            int m2 = B.GetLength(0);
            int p = B.GetLength(1);

            if (m != m2)
                throw new ArgumentException("Внутренние размеры матриц A и B должны совпадать.");
            if (C.GetLength(0) != n || C.GetLength(1) != p)
                throw new ArgumentException("Размер матрицы C должен быть n×p.");

            Parallel.For(0, n, i =>
            {
                for (int k = 0; k < p; k++)
                {
                    T acc = _ops.Zero;
                    for (int j = 0; j < m; j++)
                    {
                        acc = _ops.Add(acc, _ops.Mul(A[i, j], B[j, k]));
                    }
                    C[i, k] = acc;
                }
            });
        }

        /// <summary>
        /// Параллельная реализация алгоритма Флойда-Уоршелла.
        /// Матрица d модифицируется на месте.
        /// </summary>
        public void FloydWarshall(T[,] d)
        {
            if (d == null) throw new ArgumentNullException(nameof(d));

            int n = d.GetLength(0);
            if (d.GetLength(1) != n)
                throw new ArgumentException("Матрица должна быть квадратной.");

            for (int k = 0; k < n; k++)
            {
                int kk = k; // захватываем в локальную переменную для Parallel.For

                Parallel.For(0, n, i =>
                {
                    for (int j = 0; j < n; j++)
                    {
                        T viaK = _ops.Mul(d[i, kk], d[kk, j]);
                        if (_ops.Better(viaK, d[i, j]))
                        {
                            d[i, j] = viaK;
                        }
                    }
                });
            }
        }

        /// <summary>
        /// Флойд-Уоршелл с разузлованием пути.
        /// d — матрица стоимостей/длин.
        /// next[i,j] — следующая вершина после i на пути к j.
        /// </summary>
        public void FloydWarshallWithPath(T[,] d, int?[,] next)
        {
            if (d == null) throw new ArgumentNullException(nameof(d));
            if (next == null) throw new ArgumentNullException(nameof(next));

            int n = d.GetLength(0);
            if (d.GetLength(1) != n ||
                next.GetLength(0) != n ||
                next.GetLength(1) != n)
                throw new ArgumentException("Матрицы d и next должны быть одинакового размера n×n.");

            for (int k = 0; k < n; k++)
            {
                int kk = k;

                Parallel.For(0, n, i =>
                {
                    for (int j = 0; j < n; j++)
                    {
                        T viaK = _ops.Mul(d[i, kk], d[kk, j]);
                        if (_ops.Better(viaK, d[i, j]))
                        {
                            d[i, j] = viaK;
                            next[i, j] = next[i, kk];
                        }
                    }
                });
            }
        }

        /// <summary>
        /// Вспомогательный метод: восстановление пути по матрице next.
        /// Возвращает массив вершин от u до v (включительно) или null, если пути нет.
        /// </summary>
        public static int[] ReconstructPath(int u, int v, int?[,] next)
        {
            if (next == null) throw new ArgumentNullException(nameof(next));

            if (next[u, v] == null)
                return null;

            var path = new System.Collections.Generic.List<int> { u };
            while (u != v)
            {
                int? nxt = next[u, v];
                if (nxt == null)
                    return null; // на всякий случай
                u = nxt.Value;
                path.Add(u);
            }
            return path.ToArray();
        }
    }

    #region Конкретные реализации AmmOps<T> для разных задач

    /// <summary>
    /// Обычная арифметика над int (для демонстрации сложения/умножения матриц).
    /// </summary>
    public sealed class IntArithmeticOps : AmmOps<int>
    {
        public override int Zero => 0;
        public override int One => 1;

        public override int Add(int a, int b) => a + b;
        public override int Mul(int a, int b) => a * b;

        // Для обычной математики "лучше" можно трактовать как "меньше".
        public override bool Better(int candidate, int current) => candidate < current;
    }

    /// <summary>
    /// Булевы операции для задач связности графа.
    /// ⊕ = OR, ⊗ = AND.
    /// </summary>
    public sealed class BoolConnectivityOps : AmmOps<bool>
    {
        public override bool Zero => false; // отсутствие связи
        public override bool One => true;   // единичная связь (например, i == j)

        public override bool Add(bool a, bool b) => a || b;
        public override bool Mul(bool a, bool b) => a && b;

        // "Лучше" — это появление новой достижимости.
        public override bool Better(bool candidate, bool current) =>
            candidate && !current;
    }

    /// <summary>
    /// Кратчайшие пути в графе: ⊕ = min, ⊗ = +.
    /// Тип значений — int.
    /// </summary>
    public sealed class IntShortestPathOps : AmmOps<int>
    {
        private readonly int _inf;

        /// <param name="infinity">
        /// Значение, используемое как "бесконечность" (нет пути).
        /// Обычно достаточно int.MaxValue / 2, чтобы избежать переполнения.
        /// </param>
        public IntShortestPathOps(int infinity)
        {
            _inf = infinity;
        }

        public override int Zero => _inf;
        public override int One => 0;

        public override int Add(int a, int b) => Math.Min(a, b);

        public override int Mul(int a, int b)
        {
            if (a >= _inf || b >= _inf)
                return _inf;
            long sum = (long)a + b;
            return sum >= _inf ? _inf : (int)sum;
        }

        public override bool Better(int candidate, int current) => candidate < current;
    }

    /// <summary>
    /// Длиннейшие пути в графе: ⊕ = max, ⊗ = +.
    /// Тип значений — int.
    /// </summary>
    public sealed class IntLongestPathOps : AmmOps<int>
    {
        private readonly int _negInf;

        /// <param name="negativeInfinity">
        /// Значение, используемое как "-бесконечность" (нет пути).
        /// Например, int.MinValue / 2.
        /// </param>
        public IntLongestPathOps(int negativeInfinity)
        {
            _negInf = negativeInfinity;
        }

        public override int Zero => _negInf;
        public override int One => 0;

        public override int Add(int a, int b) => Math.Max(a, b);

        public override int Mul(int a, int b)
        {
            if (a <= _negInf || b <= _negInf)
                return _negInf;
            long sum = (long)a + b;
            if (sum <= _negInf) return _negInf;
            if (sum >= int.MaxValue) return int.MaxValue;
            return (int)sum;
        }

        public override bool Better(int candidate, int current) => candidate > current;
    }

    #endregion
}
