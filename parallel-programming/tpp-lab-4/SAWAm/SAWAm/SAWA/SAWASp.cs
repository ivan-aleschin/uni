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
            int i,j;
            for (i = _SE.si; i < _SE.si + _SE.ndp; i++)
                for (j = _SE.sj; j < _SE.sj + _SE.ndp; j++)
                    _aC[i,j] = _aA[i,j] + _aB[i,j];
        }
    }
}
