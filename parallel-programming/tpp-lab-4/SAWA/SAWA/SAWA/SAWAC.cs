using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;

namespace SAWA
{
    class SAWAC
    {
        private static int N, B, p;
        private int[] startN;
        private int[] aA, aB, aC;
        private SAWASp[] parS;
        Stopwatch t = new Stopwatch();


        public bool Init(string _N, string _B, string _p)
        {
            int i;
            if ((Int32.TryParse(_N, out N)) & (Int32.TryParse(_B, out B) & (Int32.TryParse(_p, out p))))
            {
                startN = new int[p];
                parS = new SAWASp[p];
                for (i = 0; i < p; i++)
                {
                    startN[i] = i * (N / p);
                    parS[i] = new SAWASp();
                }
                aA = new int[N];
                aB = new int[N];
                aC = new int[N];
                Random Aval = new Random();
                for (i = 0; i < N; i++)
                {
                    aA[i] = Aval.Next(B);
                    aB[i] = Aval.Next(B);
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
                _dgArr.Rows[i].Cells[0].Value = aA[i].ToString();
                _dgArr.Rows[i].Cells[1].Value = aB[i].ToString();
            }
            if (_all)
                for (i = 0; i < r; i++)
                    _dgArr.Rows[i].Cells[2].Value = aC[i].ToString();
        }
        public string SeqSum()
        {
            int i;
            t.Restart();
            for (i = 0; i < N; i++)
                aC[i] = aA[i] + aB[i];
            t.Stop();
            return t.Elapsed.ToString();

        }
        public string ParSum()
        {
            int i;
            
            Task[] tasks = new Task[p];
            t.Restart();
            for (i = 0; i < p; i++)
            {
                int ci = i;
                tasks[i] = Task.Factory.StartNew(
                    () =>
                    {
                        try
                        {
                            parS[ci].Si(aA, aB, aC, startN[ci], startN[ci] + N / p);
                        }
                        catch (Exception e)
                        {
                            MessageBox.Show(e.Message);
                        }
                    }
                    );
            }
            Task.WaitAll(tasks);
            t.Stop();
            return t.Elapsed.ToString();
        }

        public string PFSum()
        {
            ParallelOptions options = new ParallelOptions();
            options.MaxDegreeOfParallelism = -1; // -1 is for unlimited. 1 is for sequential.
            t.Restart();
            try
            {
                Parallel.For(
                        0,
                        N-1,
                        options,
                        (i) =>
                        {
                            aC[i] = aA[i] + aB[i];
                        }
                    );
            }
            // No exception is expected in this example, but if one is still thrown from a task,
            // it will be wrapped in AggregateException and propagated to the main thread.
            catch (AggregateException e)
            {
                MessageBox.Show(e.ToString());
            }
            t.Stop();
            return t.Elapsed.ToString();
        }
    }
}
