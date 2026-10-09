@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cpu-parity --target iq3s_cache_test iq_avx2_parity --parallel 6
if errorlevel 1 exit /b %errorlevel%
set STRATA_IQ_MT_MIN=1
set STRATA_IQ256_GATHER=1
C:\Strata\local-setup\target-80\build-cpu-parity\iq3s_cache_test.exe
if errorlevel 1 exit /b %errorlevel%
set STRATA_IQ_MT_MIN=2
C:\Strata\local-setup\target-80\build-cpu-parity\iq3s_cache_test.exe
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" -S C:\Strata -B C:\Strata\local-setup\target-80\build-native-off -G Ninja "-DCMAKE_MAKE_PROGRAM=C:\llama-cpp-src\toolchains\vs-buildtools\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe" -DCMAKE_BUILD_TYPE=Release -DSTRATA_PORTABLE=ON -DSTRATA_ENABLE_CUDA=OFF -DSTRATA_NATIVE_EXPERTS=OFF -DSTRATA_BUILD_TESTS=OFF
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-native-off --target strata_kernels_cpu --parallel 6
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /O2 /MT /EHsc /I C:\Strata\include C:\Strata\local-setup\target-80\native-off-smoke.cpp /Fo:C:\Strata\local-setup\target-80\native-off-smoke.obj /Fe:C:\Strata\local-setup\target-80\native-off-smoke.exe /link advapi32.lib C:\Strata\local-setup\target-80\build-native-off\strata_kernels_cpu.lib
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\native-off-smoke.exe
exit /b %errorlevel%
