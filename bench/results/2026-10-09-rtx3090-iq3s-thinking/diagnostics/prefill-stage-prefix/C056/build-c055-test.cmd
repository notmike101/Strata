@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
cl /nologo /EHsc /std:c++17 /O2 /I C:\Strata\include C:\Strata\tools\test_prefill_stage_bounds.cpp /FoC:\Strata\local-setup\target-80\c055-bounds.obj /FeC:\Strata\local-setup\target-80\c055-bounds.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\c055-bounds.exe
exit /b %errorlevel%
