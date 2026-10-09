@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /O2 /MT /EHsc /I C:\Strata\include /I "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\include" C:\Strata\src\kernels\mmvq_multi_parity.cpp /Fo:C:\Strata\local-setup\target-80\mmvq_multi_parity.obj /Fe:C:\Strata\local-setup\target-80\mmvq_multi_parity.exe /link /LIBPATH:"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\lib\x64" C:\Strata\local-setup\target-80\build-cuda86\strata_kernels.lib C:\Strata\local-setup\target-80\build-cuda86\strata_core.lib cudart.lib cudadevrt.lib advapi32.lib
exit /b %errorlevel%
