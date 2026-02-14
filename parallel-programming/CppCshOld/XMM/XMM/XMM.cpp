// XMM.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "XMM.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// The one and only application object

//CWinApp theApp;

using namespace std;

int main()
{
    int nRetCode = 0;

    HMODULE hModule = ::GetModuleHandle(nullptr);

    /*if (hModule != nullptr)
    {
        // initialize MFC and print and error on failure
        if (!AfxWinInit(hModule, nullptr, ::GetCommandLine(), 0))
        {
            // TODO: change error code to suit your needs
            wprintf(L"Fatal Error: MFC initialization failed\n");
            nRetCode = 1;
        }
        else
        {*/
            float A[8] = { 1,2,3,4,5,6,7,8 };
			float Res[8];
			float *p;
			float *r;
			int s;
			p = A;
			r = Res;
			_asm
			{
				push ECX
				push EDI
				mov EDI, p
				pxor    ymm0, ymm0
				movups  ymm1, A
				addps   ymm0, ymm1
				addps   ymm0, ymm1
				mov EDI, r
				movups Res, ymm0				
				pop EDI
				pop ECX
			}
			s = Res[0] + Res[1] + Res[2] + Res[3];
			s = s;
        }
    /*}
    else
    {
        // TODO: change error code to suit your needs
        wprintf(L"Fatal Error: GetModuleHandle failed\n");
        nRetCode = 1;
    }*/

    //return nRetCode;
}
