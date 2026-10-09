@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "CUDA_PATH=C:\Strata\local-setup\target-80\deps\cuda-13.4.2"
"%CUDA_PATH%\bin\nvcc.exe" -arch=sm_86 -O3 -std=c++17 -Xcompiler /MT C:\Strata\local-setup\target-80\cuda134-smoke.cu -o C:\Strata\local-setup\target-80\cuda134-smoke.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\cuda134-smoke.exe
exit /b %errorlevel%
