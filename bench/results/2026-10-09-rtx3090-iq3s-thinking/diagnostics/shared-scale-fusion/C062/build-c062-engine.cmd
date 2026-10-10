@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target strata shared_scale_fusion_test qfuse_gdn_test native_multi_parity shared_expert_parity gdn_parity gr_parity verify_parity --parallel 4
if errorlevel 1 exit /b %errorlevel%
exit /b 0
