@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target accepted_usage_test --parallel 4
if errorlevel 1 exit /b %errorlevel%
C:\Strata\local-setup\target-80\build-cuda86-main\accepted_usage_test.exe
exit /b %errorlevel%
