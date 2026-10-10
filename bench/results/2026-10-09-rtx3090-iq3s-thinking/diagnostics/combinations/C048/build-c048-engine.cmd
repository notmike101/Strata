@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target strata pool_affinity_test iq_avx2_parity accepted_usage_test token_barrier_test --parallel 4
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\build-cuda86-main\token_barrier_test.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\build-cuda86-main\accepted_usage_test.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\build-cuda86-main\pool_affinity_test.exe
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\build-cuda86-main\iq_avx2_parity.exe
exit /b %errorlevel%
