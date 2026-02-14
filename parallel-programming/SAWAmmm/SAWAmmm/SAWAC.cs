using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SAWA
{
    class SAWAC
    {
        public struct tSE
        {
            public int startRow;
            public int endRow;
        }

        private static int N, B, p;
        private tSE[] startN;
        private int[,] aA, aB, aC;
        private SAWASp[] parS;
        Stopwatch timer = new Stopwatch();
        private ManualResetEvent[] semaphores;

        public bool Init(string _N, string _B, string _p)
        {
            int i;
            if ((Int32.TryParse(_N, out N)) & (Int32.TryParse(_B, out B) & (Int32.TryParse(_p, out p))))
            {
                startN = new tSE[p];
                parS = new SAWASp[p];

                int baseSize = N / p;
                int remainder = N % p;
                int currentStart = 0;

                for (i = 0; i < p; i++)
                {
                    int blockSize = baseSize + (i < remainder ? 1 : 0);
                    startN[i].startRow = currentStart;
                    startN[i].endRow = currentStart + blockSize;
                    currentStart += blockSize;

                    parS[i] = new SAWASp();
                }

                aA = new int[N, N];
                aB = new int[N, N];
                aC = new int[N, N];
                Random Aval = new Random();
                for (i = 0; i < N; i++)
                    for (int j = 0; j < N; j++)
                    {
                        aA[i, j] = Aval.Next(B);
                        aB[i, j] = Aval.Next(B);
                    }

                semaphores = new ManualResetEvent[p];
                for (int k = 0; k < p; k++)
                {
                    semaphores[k] = new ManualResetEvent(false);
                }
                return true;
            }
            else
                return false;
        }

        public void Show(DataGridView _dgArr, bool _all)
        {
            int i, r;
            if (N < 20)
                r = N;
            else
                r = 100;
            _dgArr.RowCount = r;
            for (i = 0; i < r; i++)
            {
                _dgArr.Rows[i].Cells[0].Value = aA[i,0].ToString();
                _dgArr.Rows[i].Cells[1].Value = aB[i,0].ToString();
            }
            if (_all)
                for (i = 0; i < r; i++)
                    _dgArr.Rows[i].Cells[2].Value = aC[i,0].ToString();
        }

        public string SeqSum()
        {
            timer.Restart();
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++)
                    aC[i, j] = aA[i, j] + aB[i, j];
            timer.Stop();
            return timer.Elapsed.ToString();
        }

        public string ParSum()
        {
            timer.Restart();
            Task[] tasks = new Task[p];

            for (int i = 0; i < p; i++)
            {
                int ci = i;
                tasks[i] = Task.Factory.StartNew(() =>
                {

                    try
                    {
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

        public string PFSum()
        {
            ParallelOptions options = new ParallelOptions();
            options.MaxDegreeOfParallelism = -1;
            timer.Restart();

            try
            {
                Parallel.For(0, N, options, (i) =>
                {
                    for (int j = 0; j < N; j++)
                    {
                        aC[i, j] = aA[i, j] + aB[i, j];
                    }
                });
            }
            catch (AggregateException e)
            {
                MessageBox.Show(e.ToString());
            }

            timer.Stop();
            return timer.Elapsed.ToString();
        }

        public void MatSumPar()
        {
            for (int i = 0; i < p; i++)
            {
                int threadIndex = i;
                semaphores[threadIndex].Reset();

                Thread thread = new Thread(() => ProcessMatrixPart(threadIndex));
                thread.Priority = ThreadPriority.Highest;
                thread.Start();
            }
        }

        public string AVXSum()
        {
            timer.Restart();
            MatSumPar();
            Thread mtaThread = new Thread(() =>
            {
                WaitHandle.WaitAll(semaphores);
            });
            mtaThread.SetApartmentState(ApartmentState.MTA);
            mtaThread.Start();
            mtaThread.Join();
            timer.Stop();
            return timer.Elapsed.ToString();
        }


        // AVX2 горизонтально
        private unsafe void ProcessMatrixPart(int threadIndex)
        {
            try
            {
                int vectorSize = 256 / 8 / 4;
                int startRow = threadIndex * N / p;
                int endRow = (threadIndex + 1) * N / p;

                fixed (int* ptrA = aA, ptrB = aB, ptrC = aC)
                {
                    for (int row = startRow; row < endRow; row++)
                    {
                        for (int j = 0; j < N; j += vectorSize)
                        {
                            int offset = row * N + j;

                            Vector256<int> vA = Avx2.LoadVector256(ptrA + offset);
                            Vector256<int> vB = Avx2.LoadVector256(ptrB + offset);
                            Vector256<int> vResult = Avx2.Add(vA, vB);
                            Avx2.Store(ptrC + offset, vResult);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Thread {threadIndex} error: {ex.Message}");
            }
            finally
            {
                semaphores[threadIndex].Set();
            }
        }
    }
}