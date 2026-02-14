using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;

namespace CshCpp
{
    internal class CshCppWrp
    {
        public float Sum(float[] arr)
        {
            return ArrSum(arr, arr.Length);
        }

        public void SumArrays(float[] arr1, float[] arr2, float[] result)
        {
            SumArray(arr1, arr2, result, result.Length);
        }

        public void SumMatrixes(float[] arr1, float[] arr2, float[] result)
        {
            SumMatrix(arr1, arr2, result, result.Length);
        }

        [DllImport("CppAP.dll", EntryPoint = "Sum", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern float ArrSum(float[] array, int length);

        [DllImport("CppAP.dll", EntryPoint = "SumArrays", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern void SumArray(float[] arr1, float[] arr2, float[] sum, int resLength);

        [DllImport("CppAP.dll", EntryPoint = "SumMatrixes", CharSet = CharSet.Auto, SetLastError = false)]
        private static extern void SumMatrix(float[] arr1, float[] arr2, float[] sum, int resLength);
    }
}
