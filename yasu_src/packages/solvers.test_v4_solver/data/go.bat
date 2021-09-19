@echo off
rem call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64 vs2019
rem set PATH=%PATH%;%USERPROFILE%\iRIC_v4\guis\prepost\

set sname=solver.exe

echo --------------------------------------------------
echo # arguments
rem argument0 
echo %%0 = %0

rem argument1
echo %%1 = %1

rem Get directory for execute
echo --------------------------------------------------
echo # execute file path is
echo %~dp0
set exe_dir=%~dp0
echo -


rem Get current directory
echo --------------------------------------------------
echo # Current directory is
echo %cd%
set cur_dir=%cd%
rem echo %cur_dir%\out
echo -

rem execute exe
echo --------------------------------------------------
echo # Start exe
echo %date%_%time%

rem the check type of execution and run
echo # run exe
"%exe_dir%\%sname%" %1

echo # End exe
echo %date%_%time%

