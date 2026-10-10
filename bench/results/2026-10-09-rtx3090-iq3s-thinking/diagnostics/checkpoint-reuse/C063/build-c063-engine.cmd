@echo off
call "C:\llama-cpp-src\toolchains\vs-buildtools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
"C:\Strata\.venv\Scripts\cmake.exe" --build C:\Strata\local-setup\target-80\build-cuda86-main --target strata conversation_snapshot_test conversation_cache_test conversation_split_failure_test conversation_memory_test conversation_file_test conversation_validation_test qfuse_gdn_test verify_parity --parallel 4
if errorlevel 1 exit /b %errorlevel%
exit /b 0
