using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;

namespace CshCpp
{
    internal class CshCppASMWRP
    {
        public float Sum(float[] arr)
        {
            return ArrSum(arr, arr.Length);
        }
        public void SumArrays(float[] arr1, float[] arr2, float[] result)
        {
            SumXMMArray(arr1, arr2, result, result.Length);
        }

        public void SumMatrixes(float[] arr1, float[] arr2, float[] result)
        {
            SumXMMMatrix(arr1, arr2, result, result.Length);
        }

        [DllImport("CppAP.dll", EntryPoint = "SumXMM", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern float ArrSum(float[] array, int length);

        [DllImport("CppAP.dll", EntryPoint = "SumXMMArrays", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern void SumXMMArray(float[] Array1, float[] Array2, float[] Result, int length);

        [DllImport("CppAP.dll", EntryPoint = "SumXMMMatrixes", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern void SumXMMMatrix(float[] Matrix1, float[] Matrix2, float[] Result, int rows);
    }
}
