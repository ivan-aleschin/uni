using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Windows.Forms;
using System.Diagnostics;

namespace AVX2
{
    class AVX2C
    {
        Stopwatch timer = new Stopwatch();
        int[] A;
        int l;
        public void Gen(string _l)
        {
            if (Int32.TryParse(_l, out l))
            {
                A = new int[l];
                Random rnd = new Random();
                for (var i = 0; i < A.LongLength; i++)
                {
                    A[i] = 1;//(int)rnd.Next(1, 2);//
                }
                SeqSum();
                Intrinsics(A, l);
            }
        }

        public void SeqSum()
        {
            int i;
            Int64 result;
            result = 0;
            timer.Restart();
            for (i = 0; i < A.Length; i++)
                result = result + A[i];
            timer.Stop();
            MessageBox.Show(string.Format(@"Sum:{0}; Time:{1}", result, timer.Elapsed));
        }
         

        public unsafe void Intrinsics(int[] _input, int _len)
        {
            try
            {
                int vectorSize = 256 / 8 / 4;
                Vector256<int> accVector = Vector256<int>.Zero;
                Vector256<int> v = new Vector256<int>();
                int i;
                Int64 result;
                timer.Restart();
                fixed (int* ptrA = _input)
                {
                    for (i = 0; i < _len; i = i + vectorSize)
                    {
                        v = Avx2.LoadVector256(ptrA + i);
                        accVector = Avx2.Add(accVector, v);
                    }
                }

                int* temp = stackalloc int[vectorSize];
                Avx2.Store(temp, accVector);
                result = 0;
                for (int j = 0; j < vectorSize; j++)
                {
                    result = result + temp[j];
                }
                timer.Stop();
                MessageBox.Show(string.Format(@"Sum:{0}; Time:{1}", result, timer.Elapsed));
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

        }
    }
}

