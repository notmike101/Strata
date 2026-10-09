@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
cl /nologo /O2 /EHsc /std:c++17 /I C:\Strata\include C:\Strata\local-setup\target-80\C025-spec-gate-test.cpp /Fe:C:\Strata\local-setup\target-80\C025-spec-gate-test.exe /Fo:C:\Strata\local-setup\target-80\C025-spec-gate-test.obj
exit /b %errorlevel%
