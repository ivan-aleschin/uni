#include <cstdint>
#include <cmath>

#ifdef __cplusplus
extern "C" {
#endif

	__declspec(dllexport) float Sum(float *Array, int length) {
		float result = 0;
		
		for (auto i = 0; i < length; ++i) {
			result += Array[i];
		}
		return result;
	}

	__declspec(dllexport) void SumArrays(float* arr1, float* arr2, float* sum, int resLength) {
		for (int i = 0; i < resLength; ++i) {
			sum[i] = arr1[i] + arr2[i];
		}
	}

	__declspec(dllexport) void SumMatrixes(float* arr1, float* arr2, float* sum, int resLength) {

		int length = sqrt(resLength);

		for (int i = 0; i < length; ++i) {
			for (int j = 0; j < length; ++j) {
				sum[i * length + j] = arr1[i * length + j] + arr2[i * length + j];
			}
		}
	}


	__declspec(dllexport) float SumXMM(float* Array, int length)
	{
		float result = 0;		
		float Res[4];
		int len = length * 4;
		float *p;
		p = Array;
		__asm
		{
			push ECX
			push EDI
			push ESI
			mov EDI, len
			mov ECX, 0 //xor ECX, ECX
			mov ESI, p
			pxor    xmm0, xmm0 //| 0 | 0 | 0 | 0 |
			Back :
				movups  xmm1, [ESI][ECX] //Array[ECX]
				addps   xmm0, xmm1
				add     ECX, 16
				cmp     ECX, EDI
			jne      Back
			movups Res, xmm0
			pop ESI
			pop EDI
			pop ECX
		}

		result = Res[0] + Res[1] + Res[2] + Res[3];
		return result;//len;
	}	

	__declspec(dllexport) void SumXMMArrays(float* Array1, float* Array2, float* Result, int length)
	{
		int len = length * 4;
		__asm
		{
			push ECX
			push EDI
			push ESI
			push EBX

			mov EDI, len
			mov ECX, 0
			mov ESI, Array1    
			mov EBX, Array2    
			mov EDX, Result   

			BackAdd :
				movups  xmm0, [ESI][ECX]  
				movups  xmm1, [EBX][ECX]  
				addps   xmm0, xmm1        
				movups  [EDX][ECX], xmm0  

				add     ECX, 16           
				cmp     ECX, EDI
				jne     BackAdd

				pop EBX
				pop ESI
				pop EDI
				pop ECX
		}
	}

	__declspec(dllexport) void SumXMMMatrixes(float* Matrix1, float* Matrix2, float* Result, int length)
	{
		int len = length * 4;
		__asm
		{
			push ECX
			push EDI
			push ESI
			push EBX

			mov EDI, len
			mov ECX, 0
			mov ESI, Matrix1
			mov EBX, Matrix2
			mov EDX, Result

			BackAdd :
			movups  xmm0, [ESI][ECX]
				movups  xmm1, [EBX][ECX]
				addps   xmm0, xmm1
				movups[EDX][ECX], xmm0

				add     ECX, 16
				cmp     ECX, EDI
				jne     BackAdd

				pop EBX
				pop ESI
				pop EDI
				pop ECX
		}
	}

#ifdef __cplusplus
}
#endif