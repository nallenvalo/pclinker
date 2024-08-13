@echo off
set LOGDIR="C:\Users\microscope\Desktop\skeletalStimLogs\ErrorCallback"
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set TIME=%time:~0,2%%time:~3,2%%time:~6,2%
set FILENAME=logfile_%DATE%_%TIME%.txt
set LOGFILE=%LOGDIR%\%FILENAME%

:: Remove leading spaces from time variables (for hours less than 10)
set TIME=%TIME: =0%

call C:\Users\microscope\webApp\.venv\Scripts\activate.bat
start /HIGH python C:\Users\microscope\webApp\SkelStim_TDMS_SQL_Flask_NG.py 1 1>> %LOGFILE% 2>&1
