using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;

namespace SAWA
{
    class SAWAC
    {
        public struct tSE
        {
            public int si;
            public int sj;
            public int ndp;
        }

        tSE rSE;
        private static int N, B, p;
        tSE[] startN;  // ОДНОМЕРНЫЙ массив для горизонтального распределения
        private int[,] aA, aB, aC;
        private SAWASp[] parS;  // ОДНОМЕРНЫЙ массив

        Stopwatch timer = new Stopwatch();

        public bool Init(string _N, string _B, string _p)
        {
            int i, j;
            if ((Int32.TryParse(_N, out N)) & (Int32.TryParse(_B, out B) & (Int32.TryParse(_p, out p))))
            {
                parS = new SAWASp[p];    // ОДНОМЕРНЫЙ
                startN = new tSE[p];     // ОДНОМЕРНЫЙ

                // ГОРИЗОНТАЛЬНОЕ РАСПРЕДЕЛЕНИЕ
                for (i = 0; i < p; i++)
                {
                    parS[i] = new SAWASp();
                    startN[i].si = i * (N / p);  // начальная строка
                    startN[i].sj = 0;            // ВСЕГДА с 0 столбца!
                    startN[i].ndp = N / p;       // количество строк
                }

                aA = new int[N, N];
                aB = new int[N, N];
                aC = new int[N, N];
                Random Aval = new Random();
                for (i = 0; i < N; i++)
                    for (j = 0; j < N; j++)
                    {
                        aA[i, j] = Aval.Next(B);
                        aB[i, j] = Aval.Next(B);
                    }
                return true;
            }
            else
                return false;
        }

        public void Show(DataGridView _dgArr, bool _all)
        {
            int i, j, r;
            if (N < 20)
                r = N;
            else
                r = 100;
            _dgArr.RowCount = r;
            for (i = 0; i < r; i++)
                for (j = 0; j < N; j++)
                {
                    _dgArr.Rows[i].Cells[0].Value = aA[i, j].ToString();
                    _dgArr.Rows[i].Cells[1].Value = aB[i, j].ToString();
                }
            if (_all)
                for (i = 0; i < r; i++)
                    for (j = 0; j < N; j++)
                        _dgArr.Rows[i].Cells[2].Value = aC[i, j].ToString();
        }

        public string SeqSum()
        {
            int i, j;

            timer.Restart();
            for (i = 0; i < N; i++)
                for (j = 0; j < N; j++)
                    aC[i, j] = aA[i, j] + aB[i, j];
            timer.Stop();
            return timer.Elapsed.ToString();
        }

        public string ParSum()
        {
            timer.Restart();

            // Создаем P задач (горизонтальное распределение)
            Task[] tasks = new Task[p];
            for (int i = 0; i < p; i++)
            {
                int ci = i;
                tasks[i] = Task.Factory.StartNew(() =>
                {
                    try
                    {
                        // Каждый процесс обрабатывает свою горизонтальную полосу
                        parS[ci].Si(aA, aB, aC, startN[ci]);
                    }
                    catch (Exception e)
                    {
                        MessageBox.Show(e.Message);
                    }
                });
            }

            Task.WaitAll(tasks);
            timer.Stop();
            return timer.Elapsed.ToString();
        }

        public string AVXSum()
        {
            timer.Restart();

            Parallel.For(0, p, new ParallelOptions { MaxDegreeOfParallelism = p },
                threadIdx =>
                {
                    // Горизонтальное распределение
                    int startRow = threadIdx * (N / p);
                    int endRow = (threadIdx == p - 1) ? N : startRow + (N / p);

                    for (int i = startRow; i < endRow; i++)
                    {
                        for (int j = 0; j < N; j += 8)
                        {
                            if (Avx2.IsSupported && j + 7 < N)
                            {
                                unsafe
                                {
                                    fixed (int* ptrA = &aA[i, j])
                                    fixed (int* ptrB = &aB[i, j])
                                    fixed (int* ptrC = &aC[i, j])
                                    {
                                        var vecA = Avx2.LoadVector256(ptrA);
                                        var vecB = Avx2.LoadVector256(ptrB);
                                        var vecResult = Avx2.Add(vecA, vecB);
                                        Avx2.Store(ptrC, vecResult);
                                    }
                                }
                            }
                            else
                            {
                                for (int k = j; k < Math.Min(j + 8, N); k++)
                                {
                                    aC[i, k] = aA[i, k] + aB[i, k];
                                }
                            }
                        }
                    }
                });

            timer.Stop();
            return timer.Elapsed.ToString();
        }

        // Метод для проверки распределения
        public string GetDistributionInfo()
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("Горизонталное распределение матриц:");
            for (int i = 0; i < p; i++)
            {
                sb.AppendLine($"Процесс {i}: строки [{startN[i].si}-{startN[i].si + startN[i].ndp - 1}], Все столбцы");
            }
            return sb.ToString();
        }
    }
}