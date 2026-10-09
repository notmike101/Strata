@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "CUDA_PATH=C:\Strata\local-setup\target-80\deps\cuda-13.4.2"
set "PATH=%CUDA_PATH%\bin;%PATH%"
set "STRATA_CMAKE=C:\Strata\.venv\Scripts\cmake.exe"
set "STRATA_BUILD=C:\Strata\local-setup\target-80\build-cuda134-control"
"%STRATA_CMAKE%" -S C:\Strata -B "%STRATA_BUILD%" -G Ninja -DCMAKE_MAKE_PROGRAM=C:/llama-cpp-src/toolchains/vs-buildtools/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_COMPILER=C:/Strata/local-setup/target-80/deps/cuda-13.4.2/bin/nvcc.exe -DCUDAToolkit_ROOT=C:/Strata/local-setup/target-80/deps/cuda-13.4.2 -DCMAKE_CUDA_ARCHITECTURES=86 -DSTRATA_ENABLE_CUDA=ON -DSTRATA_ENABLE_HIP=OFF -DSTRATA_ENABLE_SYCL=OFF -DSTRATA_PORTABLE=ON -DSTRATA_NATIVE_EXPERTS=ON -DSTRATA_BUILD_TESTS=ON -DSTRATA_GGML_DIR=C:/Strata/local-setup/target-80/deps/llama.cpp-3cf03257f219afbe7334045ff7c6a06ac68c627d
if errorlevel 1 exit /b %errorlevel%
"%STRATA_CMAKE%" --build "%STRATA_BUILD%" --target strata iq_avx2_parity pool_tasks_test iq_avx2_dispatch_test --parallel 6
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\ctest.exe" --test-dir "%STRATA_BUILD%" -R "iq_avx2_parity|pool_tasks_test|iq_dispatch" --output-on-failure
exit /b %errorlevel%
