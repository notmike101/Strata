@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /O2 /MT /I C:\Strata\include C:\Strata\tests\core\accepted_usage.cpp /FoC:\Strata\local-setup\target-80\c046-test.obj /FeC:\Strata\local-setup\target-80\c046-test.exe
exit /b %errorlevel%
