@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "CUDA_PATH=C:\Strata\local-setup\target-80\deps\cuda-13.4.2"
set "PATH=C:\Strata\.venv\Lib\site-packages\nvidia\cu13\bin\x86_64;%CUDA_PATH%\bin\x64;%PATH%"
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda134-control --target native_multi_parity mmvq_multi_parity kv_stream_parity verify_batch_parity --parallel 6
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\ctest.exe" --test-dir C:\Strata\local-setup\target-80\build-cuda134-control -R "^(native_multi_parity|mmvq_multi_parity|kv_stream_parity|verify_batch_parity)$" --output-on-failure
exit /b %errorlevel%
