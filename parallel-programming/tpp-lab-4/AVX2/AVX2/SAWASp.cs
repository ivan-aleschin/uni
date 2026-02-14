using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SAWA
{
    class SAWASp
    {
        public void Si(int[,] _aA, int[,] _aB, int[,] _aC, SAWAC.tSE _SE)
        {
            // Горизонтальное распределение матриц
            for (int i = _SE.si; i < _SE.si + _SE.ndp; i++)
                for (int j = 0; j < _aA.GetLength(1); j++)  
                    _aC[i, j] = _aA[i, j] + _aB[i, j];
        }
    }
}