using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SAWA
{
    class SAWASp
    {
        public void Si(int[] _aA, int[] _aB, int[] _aC, int _start, int _end)
        {
            int i;
            for (i = _start; i < _end; i++)
                _aC[i] = _aA[i] + _aB[i];
        }
    }
}
