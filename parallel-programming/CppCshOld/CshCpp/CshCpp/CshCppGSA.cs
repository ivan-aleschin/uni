using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;

namespace CshCpp
{
    class CshCppGSA
    {
        CshCppWrp ap = new CshCppWrp();
        CshCppASMWRP asmp = new CshCppASMWRP();

        float res;
        private float[] Arr1;
        private float[] Arr2;
        private float[] res1;
        private float[] Matr1;
        private float[] Matr2;
        private float[] res2;

        public void Gen(int _l)
        {
            res = 0;

            Arr1 = new float[_l];
            Arr2 = new float[_l];
            res1 = new float[_l];

            Matr1 = new float[_l * _l];
            Matr2 = new float[_l * _l];
            res2 = new float[_l * _l];

            for (var i = 0; i < _l; ++i)
            {
                Arr1[i] = (float)0.000000001;
                Arr2[i] = (float)0.000000001;

            }

            for (var i = 0; i < _l * _l; ++i)
            {
                Matr1[i] = (float)0.000000001;
                Matr2[i] = (float)0.000000001;
            }
        }

        public string SumCsh()
        {
            int i;

            if (Arr1 == null)
            {
                return @"Array not generated!";
            }
            else
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                for (i = 0; i < Arr1.LongLength; ++i)
                {
                    res = res + Arr1[i];
                }
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res, timer.Elapsed);
            }

        }

        public string SumCppDLL()
        {
            if (Arr1 == null)
            {
                return @"Array not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                res = ap.Sum(Arr1);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res, timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }

        public string SumCppDLLasm()
        {
            if (Arr1 == null)
            {
                return @"Array not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                res = asmp.Sum(Arr1);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res, timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }

        public string SumCshArrays()
        {
            int i;

            if (Arr1 == null || Arr2 == null || res1 == null)
            {
                return @"Arrays not generated!";
            }
            else
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                for (i = 0; i < res1.LongLength; ++i)
                {
                    res1[i] = Arr2[i] + Arr1[i];
                }
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res1[0], timer.Elapsed);
            }

        }

        public string SumCppArrays()
        {
            if (Arr1 == null || Arr2 == null || res1 == null)
            {
                return @"Arrays not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                ap.SumArrays(Arr1, Arr2, res1);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res1[0], timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }

        public string SumAsmArrays()
        {
            if (Arr1 == null || Arr2 == null || res1 == null)
            {
                return @"Arrays not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                asmp.SumArrays(Arr1, Arr2, res1);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res1[0], timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }

        public string SumCshMatrixes()
        {
            int i;

            if (Matr1 == null || Matr2 == null || res2 == null)
            {
                return @"Matrixes not generated!";
            }
            else
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                for (i = 0; i < res2.LongLength; ++i)
                {
                    res2[i] = Matr2[i] + Matr1[i];
                }
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res2[0], timer.Elapsed);
            }

        }

        public string SumCppMatrixes()
        {
            if (Matr1 == null || Matr2 == null || res2 == null)
            {
                return @"Matrixes not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                ap.SumMatrixes(Matr1, Matr2, res2);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res2[0], timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }

        public string SumAsmMatrixes()
        {
            if (Matr1 == null || Matr2 == null || res2 == null)
            {
                return @"Matrixes not generated!";
            }
            try
            {
                Stopwatch timer = new Stopwatch();
                timer.Start();
                asmp.SumMatrixes(Matr1, Matr2, res2);
                timer.Stop();
                return string.Format(@"Sum:{0}; Time:{1}", res2[0], timer.Elapsed);
            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }
    }
}
