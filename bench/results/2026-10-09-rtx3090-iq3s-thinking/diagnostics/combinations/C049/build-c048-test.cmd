@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
cl /nologo /EHsc /std:c++17 /O2 /I C:\Strata\include C:\Strata\tests\core\token_barrier.cpp /FoC:\Strata\local-setup\target-80\token_barrier.obj /FeC:\Strata\local-setup\target-80\token_barrier_test.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\token_barrier_test.exe
exit /b %errorlevel%
