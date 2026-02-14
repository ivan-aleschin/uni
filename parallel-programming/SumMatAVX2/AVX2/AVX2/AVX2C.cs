using System;
using System.Diagnostics;
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;
using System.Windows.Forms;

namespace AVX2
{
    class AVX2C
    {
        private readonly Stopwatch timer = new Stopwatch();
        private int[] A = Array.Empty<int>();
        private int l;

        public void GenArr(string _l)
        {
            if (!int.TryParse(_l, out l) || l <= 0)
            {
                MessageBox.Show("Введите корректную длину массива (> 0).");
                return;
            }

            A = new int[l];

            // Инициализация (для честного замера можно использовать случайные значения)
            for (int i = 0; i < A.Length; i++)
                A[i] = 1;

            SeqSum();
            Intrinsics(A, A.Length);
        }

        public void SeqSum()
        {
            long result = 0;
            timer.Restart();
            for (int i = 0; i < A.Length; i++)
                result += A[i];
            timer.Stop();

            MessageBox.Show($"[Скалярно] Sum: {result}; Time: {timer.Elapsed}");
        }

        public unsafe void Intrinsics(int[] input, int len)
        {
            if (input == null || len <= 0)
            {
                MessageBox.Show("Пустой массив для Intrinsics.");
                return;
            }

            if (!Avx2.IsSupported)
            {
                MessageBox.Show("AVX2 не поддерживается на этом процессоре.");
                return;
            }

            const int Vec = 8; // Vector256<int>.Count
            long total = 0;
            Vector256<long> acc64 = Vector256<long>.Zero;

            timer.Restart();
            fixed (int* ptr = input)
            {
                int i = 0;

                // Векторная часть: суммируем в 64-битные lane’ы, чтобы исключить переполнение
                for (; i + Vec <= len; i += Vec)
                {
                    Vector256<int> v32 = Avx2.LoadVector256(ptr + i);

                    Vector128<int> lo32 = v32.GetLower();
                    Vector128<int> hi32 = v32.GetUpper();

                    Vector256<long> lo64 = Avx2.ConvertToVector256Int64(lo32);
                    Vector256<long> hi64 = Avx2.ConvertToVector256Int64(hi32);

                    acc64 = Avx2.Add(acc64, lo64);
                    acc64 = Avx2.Add(acc64, hi64);
                }

                // Хвост
                for (; i < len; i++)
                    total += ptr[i];
            }

            // Горизонтальная сумма acc64 (в Vector256<long> 4 lane’а)
            long* tmp = stackalloc long[4];
            Avx2.Store(tmp, acc64);
            total += tmp[0] + tmp[1] + tmp[2] + tmp[3];

            timer.Stop();
            MessageBox.Show($"[AVX2] Sum: {total}; Time: {timer.Elapsed}");
        }
    }
}
