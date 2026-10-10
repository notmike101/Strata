@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "PATH=C:\Strata\.venv\Lib\site-packages\nvidia\cu13\bin\x86_64;%PATH%"
cd /d C:\Strata\local-setup\target-80\build-cuda86-main
cl /nologo /std:c++20 /O2 /EHsc /MT /I C:\Strata\include /I "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\include" /Fo..\c055-footprint.obj ..\c055-footprint.cpp /Fe..\c055-footprint.exe /link /LIBPATH:"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\lib\x64" strata_prefill.lib strata_engine.lib strata_kernels.lib strata_core.lib strata_kernels_cpu.lib ggml\src\ggml-cpu.lib cublas.lib cublasLt.lib strata_mmq.lib cudart.lib ggml\src\ggml-base.lib cudadevrt.lib kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib
if errorlevel 1 exit /b %errorlevel%
..\c055-footprint.exe C:\models\Qwen3.8-Flash-Next\Strata\packs\iq3_s > ..\c055-footprint.csv
exit /b %errorlevel%
