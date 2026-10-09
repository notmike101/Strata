@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
set "PATH=C:\Strata\.venv\Lib\site-packages\nvidia\cu13\bin\x86_64;%PATH%"
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target exchange_storage_test file_expert_source_test --parallel 6
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\ctest.exe" --test-dir C:\Strata\local-setup\target-80\build-cuda86-main -R "^(exchange_storage_test|file_expert_source_test)$" --output-on-failure
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\local-setup\target-80\build-cuda86-main\file_expert_source_test.exe" --rotation-gpu
exit /b %errorlevel%
