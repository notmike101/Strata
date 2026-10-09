@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3"
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target strata iq3s_cache_test iq_avx2_parity pool_tasks_test iq_avx2_dispatch_test --parallel 6
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\ctest.exe" --test-dir C:\Strata\local-setup\target-80\build-cuda86-main -R "iq3s_cache_test|iq_avx2_parity|pool_tasks_test|iq_dispatch" --output-on-failure
exit /b %errorlevel%
