@echo off
REM Try to compile with g++, otherwise instruct user to use cl or CMake
echo Building with g++...
g++ -std=c++17 L3.1.cpp -O2 -o l3_1.exe 2>compile_gpp_1.log
g++ -std=c++17 L3.3sp.cpp -O2 -o l3_3sp.exe 2>compile_gpp_3.log
if exist l3_1.exe (echo l3_1.exe built) else (echo g++ build for L3.1 failed - see compile_gpp_1.log)
if exist l3_3sp.exe (echo l3_3sp.exe built) else (echo g++ build for L3.3sp failed - see compile_gpp_3.log)

REM Create a small binary test file using PowerShell
echo Creating test binary test.bin...
powershell -Command "[IO.File]::WriteAllBytes('test.bin',[byte[]](0x00,0x01,0x68,0x65,0x6C,0x6C,0x6F,0xFF))"
echo Running L3.1 encode/decode test...
if exist l3_1.exe (
    l3_1.exe encode test.bin archive_l3_1.bin
    l3_1.exe decode archive_l3_1.bin out_l3_1.bin
    fc /b test.bin out_l3_1.bin
) else (
    echo Skipping L3.1 tests because l3_1.exe not found.
)

echo Running L3.3sp encode/decode test (single file)...
if exist l3_3sp.exe (
    l3_3sp.exe encode test.bin archive_l3_3sp.bin
    l3_3sp.exe decode archive_l3_3sp.bin out_l3_3sp.bin
    fc /b test.bin out_l3_3sp.bin
) else (
    echo Skipping L3.3sp file tests because l3_3sp.exe not found.
)

echo Creating test directory tdir...
if not exist tdir md tdir
echo dir file>tdir\a.txt
if not exist tdir\sub md tdir\sub
powershell -Command "[IO.File]::WriteAllBytes('tdir\\sub\\b.bin',[byte[]](0x10,0x20,0x30))"

echo Running L3.3sp encode/decode test (directory)...
if exist l3_3sp.exe (
    l3_3sp.exe encode tdir archive_tdir.r3
    if not exist outdir md outdir
    l3_3sp.exe decode archive_tdir.r3 outdir
    echo Comparing one file:
    fc /b tdir\a.txt outdir\tdir\a.txt
) else (
    echo Skipping L3.3sp directory tests because l3_3sp.exe not found.
)

echo Test script finished.
pause
