using System;
using System.Collections;
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
        public struct tSE
        {
            public int si;
            public int sj;
            public int ndp;
        }
        tSE rSE;
        private static int N, B, p;
        tSE[,] startN;
        private int[,] aA, aB, aC;
        private SAWASp[,] parS;

        Stopwatch timer = new Stopwatch();

        public bool Init(string _N, string _B, string _p)
        {
            int i, j;
            if ((Int32.TryParse(_N, out N)) & (Int32.TryParse(_B, out B) & (Int32.TryParse(_p, out p))))
            {
                parS = new SAWASp[p,p];
                startN = new tSE[p, p];
                for (i = 0; i < p; i++)
                {                    ;
                    for (j = 0; j < p; j++)
                    {
                        parS[i, j] = new SAWASp();
                        startN[i,j].si = i * (N / p);
                        startN[i, j].sj = j * (N / p);
                        startN[i, j].ndp = N / p;
                    }
                    
                }
                aA = new int[N, N];
                aB = new int[N, N];
                aC = new int[N, N];
                Random Aval = new Random();
                for (i = 0; i < N; i++)
                    for (j = 0; j < N; j++)
                    {
                        aA[i,j] = Aval.Next(B);
                        aB[i,j] = Aval.Next(B);
                    }
                return true;
            }
            else
                return false;
        }
        public void Show(DataGridView _dgArr, bool _all)
        {
            /*int i, r;
            if (N < 20)
                r = N;
            else
                r = 100;
            _dgArr.RowCount = r;
            for (i = 0; i < r; i++)
            {
                //_dgArr.Rows[i].Cells[0].Value = aA[i].ToString();
                //_dgArr.Rows[i].Cells[1].Value = aB[i].ToString();
            }
            if (_all)
                for (i = 0; i < r; i++)
                    //_dgArr.Rows[i].Cells[2].Value = aC[i].ToString();*/
        }
        public string SeqSum()
        {
            int i, j;

            //timer.Reset();
            TimeSpan dt = new TimeSpan();
            DateTime ts;
            DateTime te;
            ts = DateTime.Now;
            for (i = 0; i < N; i++)
                for (j = 0; j < N; j++)
                    aC[i,j] = aA[i,j] + aB[i,j];
            te = DateTime.Now;
            dt = te - ts;
            return dt.ToString();
            //timer.Stop();
            //return timer.Elapsed.ToString();
            //MessageBox.Show(string.Format(@"Time:{0}", timer.Elapsed));//MessageBox.Show

        }
        public string ParSum()
        {
            int i,j;

            //timer.Reset();
            TimeSpan dt = new TimeSpan();
            DateTime ts;
            DateTime te;
            
            ts = DateTime.Now;
            Task[] tasks = new Task[p];
            for (i = 0; i < p; i++)
                for (j = 0; j < p; j++)
                {
                int ci = i;
                int cj = j;
                tasks[i] = Task.Factory.StartNew(
                    () =>
                    {
                        try
                        {
                            parS[ci,cj].Si(aA, aB, aC, startN[ci,cj]);
                        }
                        catch (Exception e)
                        {
                            MessageBox.Show(e.Message);
                        }
                    }
                    );
            }
            Task.WaitAll(tasks);
            te = DateTime.Now;
            dt = te - ts;

            timer.Stop();
            //return timer.Elapsed.ToString();
            return dt.ToString();
        }
    }
}
