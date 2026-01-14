@echo off
REM Wrapper script to compile C files with GCC on MSYS2
REM This script sets up the necessary PATH for GCC to work properly

REM Add GCC directories to PATH
set PATH=C:\msys64\mingw64\libexec\gcc\x86_64-w64-mingw32\15.2.0;C:\msys64\mingw64\bin;%PATH%

REM Run GCC with the provided arguments
C:\msys64\mingw64\bin\gcc.exe %*
