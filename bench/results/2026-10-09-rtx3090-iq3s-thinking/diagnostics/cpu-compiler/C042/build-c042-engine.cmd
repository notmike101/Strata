@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" -S C:\Strata -B C:\Strata\local-setup\target-80\build-cuda86-main -DSTRATA_CLANG_IQ3S=ON -DSTRATA_CLANG_CL_COMPILER=C:/llama-cpp-src/toolchains/vs-buildtools/VC/Tools/Llvm/x64/bin/clang-cl.exe
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target strata iq_avx2_parity --parallel 4
exit /b %errorlevel%
