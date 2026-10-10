@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\llama-cpp-src\toolchains\vs-buildtools\VC\Tools\Llvm\x64\bin\clang-cl.exe" /nologo /std:c++20 /O2 /MT /EHsc /arch:AVX2 /fp:precise /clang:-ffp-contract=off /DSTRATA_AVXVNNI=0 /I C:\Strata /I C:\Strata\include /I C:\Strata\third_party\ggml /c C:\Strata\local-setup\target-80\c040-clang.cpp /FoC:\Strata\local-setup\target-80\c040-clang.obj
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /O2 /MT /EHsc /arch:AVX2 /I C:\Strata /I C:\Strata\include /I C:\Strata\local-setup\target-80\deps\llama.cpp-3cf03257f219afbe7334045ff7c6a06ac68c627d\ggml\include /I C:\Strata\local-setup\target-80\deps\llama.cpp-3cf03257f219afbe7334045ff7c6a06ac68c627d\ggml\src C:\Strata\local-setup\target-80\c040-actual.cpp /Fo:C:\Strata\local-setup\target-80\c040-actual.obj /Fe:C:\Strata\local-setup\target-80\c040-actual.exe C:\Strata\local-setup\target-80\c040-clang.obj /link advapi32.lib C:\Strata\local-setup\target-80\build-cuda86\strata_core.lib C:\Strata\local-setup\target-80\build-cuda86\strata_kernels_cpu.lib C:\Strata\local-setup\target-80\build-cuda86\ggml\src\ggml-cpu.lib C:\Strata\local-setup\target-80\build-cuda86\ggml\src\ggml-base.lib
exit /b %errorlevel%
