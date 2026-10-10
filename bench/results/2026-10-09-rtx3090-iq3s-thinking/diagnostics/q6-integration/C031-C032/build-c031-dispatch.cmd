@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3"
"%CUDA_PATH%\bin\nvcc.exe" -arch=sm_86 -O3 --use_fast_math -std=c++20 -Xcompiler /MT -I C:\Strata\include C:\Strata\tools\test_q6_onewarp_dispatch.cu -o C:\Strata\local-setup\target-80\c031-dispatch.exe -L C:\Strata\local-setup\target-80\build-cuda86 -l strata_kernels -l strata_core -l advapi32
exit /b %errorlevel%
