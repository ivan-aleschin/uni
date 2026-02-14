using System;
using System.Diagnostics;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Runtime.InteropServices; // GCHandle

namespace AVX2Mat
{
    internal class AVX2MatDisp
    {
        private int N, p;
        private int[,] A = new int[0, 0];
        private int[,] B = new int[0, 0];
        private int[,] C = new int[0, 0];
        private readonly Stopwatch timer = new Stopwatch();

        public AVX2MatDisp() { }

        /// <summary>
        /// Генерация матриц N x N, сложение в C с динамическим распределением работы между потоками.
        /// </summary>
        public bool GenAndSum(string _N, string _p)
        {
            if (!int.TryParse(_N, out N) || N <= 0 ||
                !int.TryParse(_p, out p) || p <= 0)
            {
                MessageBox.Show("Введите корректные N (>0) и p (>0).");
                return false;
            }

            A = new int[N, N];
            B = new int[N, N];
            C = new int[N, N];

            // Инициализация тестовыми данными
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++)
                {
                    A[i, j] = 1;
                    B[i, j] = 1;
                }

            try
            {
                timer.Restart();
                var elapsed = AddMatricesSIMD_Dynamic(p, 256 * 1024); // 256KB чанки
                timer.Stop();

                MessageBox.Show($"Время для {p} потоков: {elapsed}");
                return true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Динамическое распределение работы на чанках + AVX2.
        /// ВНИМАНИЕ: для использования указателей внутри лямбды массивы пинятся через GCHandle.
        /// </summary>
        private unsafe TimeSpan AddMatricesSIMD_Dynamic(int requestedP, int chunkBytes)
        {
            if (!Avx2.IsSupported)
                throw new PlatformNotSupportedException("AVX2 не поддерживается на этом процессоре.");

            if (A.GetLength(0) != A.GetLength(1) ||
                B.GetLength(0) != B.GetLength(1) ||
                C.GetLength(0) != C.GetLength(1))
                throw new ArgumentException("Матрицы должны быть квадратными.");

            int n0 = A.GetLength(0), n1 = A.GetLength(1);
            if (n0 != B.GetLength(0) || n1 != B.GetLength(1) ||
                n0 != C.GetLength(0) || n1 != C.GetLength(1))
                throw new ArgumentException("Размеры матриц A, B и C должны совпадать.");

            int total = n0 * n1;
            if (total == 0) return TimeSpan.Zero;

            const int Vec = 8; // Vector256<int>.Count
            int maxDeg = Math.Max(1, Math.Min(requestedP, Environment.ProcessorCount));

            // Размер чанка (в элементах), кратный ширине вектора.
            int chunkElems = Math.Max(Vec * 16, (chunkBytes / sizeof(int) / Vec) * Vec);
            if (chunkElems <= 0) chunkElems = Vec * 16;

            int next = 0;

            // Пинование массивов на время параллельного участка
            GCHandle hA = default, hB = default, hC = default;
            try
            {
                hA = GCHandle.Alloc(A, GCHandleType.Pinned);
                hB = GCHandle.Alloc(B, GCHandleType.Pinned);
                hC = GCHandle.Alloc(C, GCHandleType.Pinned);

                // Базовые адреса первых элементов
                IntPtr baseA = hA.AddrOfPinnedObject();
                IntPtr baseB = hB.AddrOfPinnedObject();
                IntPtr baseC = hC.AddrOfPinnedObject();

                var sw = Stopwatch.StartNew();

                Parallel.For(0, maxDeg, new ParallelOptions { MaxDegreeOfParallelism = maxDeg }, _ =>
                {
                    // Приводим к указателям ЛОКАЛЬНО в теле лямбды (никаких fixed-локалов тут нет)
                    int* pA = (int*)baseA;
                    int* pB = (int*)baseB;
                    int* pC = (int*)baseC;

                    for (; ; )
                    {
                        int start = Interlocked.Add(ref next, chunkElems) - chunkElems;
                        if (start >= total) break;

                        int end = Math.Min(start + chunkElems, total);

                        int i = start;
                        // Векторная часть чанка
                        for (; i + Vec <= end; i += Vec)
                        {
                            var va = Avx2.LoadVector256(pA + i);
                            var vb = Avx2.LoadVector256(pB + i);
                            var vr = Avx2.Add(va, vb);
                            Avx2.Store(pC + i, vr);
                        }
                        // Хвост чанка
                        for (; i < end; i++)
                            pC[i] = pA[i] + pB[i];
                    }
                });

                sw.Stop();
                return sw.Elapsed;
            }
            finally
            {
                if (hA.IsAllocated) hA.Free();
                if (hB.IsAllocated) hB.Free();
                if (hC.IsAllocated) hC.Free();
            }
        }

        /// <summary>
        /// Выводит первые 8x8 элементов (или меньше, если N < 8) в три DataGridView.
        /// Считается, что гриды уже имеют нужное число строк/столбцов.
        /// </summary>
        public void ShowMatrices(DataGridView _A, DataGridView _B, DataGridView _C)
        {
            if (A.Length == 0) return;

            int m = Math.Min(8, N);
            for (int i = 0; i < m; i++)
                for (int j = 0; j < m; j++)
                {
                    _A.Rows[i].Cells[j].Value = A[i, j].ToString();
                    _B.Rows[i].Cells[j].Value = B[i, j].ToString();
                    _C.Rows[i].Cells[j].Value = C[i, j].ToString();
                }
        }
    }
}
