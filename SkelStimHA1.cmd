@echo off
set ERROR_LOGDIR="C:\Users\microscope\Desktop\skeletalStimLogs\ErrorCallback"
set SUCCESS_LOGDIR="C:\Users\microscope\Desktop\skeletalStimLogs\CallBack"
set TEMPLOG_ERROR="C:\Users\microscope\Desktop\skeletalStimLogs\temp_HA1_log_error.txt"
set TEMPLOG_SUCCESS="C:\Users\microscope\Desktop\skeletalStimLogs\temp_HA1_log_success.txt"

set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set TIME=%time:~0,2%%time:~3,2%%time:~6,2%
:: Remove leading spaces from time variables (for hours less than 10)
set TIME=%TIME: =0%
set FILENAME=logfile_HA1_%DATE%_%TIME%.txt

call C:\Users\microscope\webApp\.venv\Scripts\activate.bat

cd C:\Users\microscope\webApp

:: Run the Python script and redirect stdout and stderr to separate temporary log files
python C:\Users\microscope\webApp\SkelStim_TDMS_SQL_Flask_NG.py 1 1> %TEMPLOG_SUCCESS% 2> %TEMPLOG_ERROR%

:: Check if the temporary error log file is empty
for %%A in (%TEMPLOG_ERROR%) do if %%~zA neq 0 (
    :: If the error log file is not empty, move it to the error log directory and delete the success log file
    move %TEMPLOG_ERROR% %ERROR_LOGDIR%\%FILENAME%
    del %TEMPLOG_SUCCESS%
) else (
    :: If the error log file is empty, move the success log file to the success log directory and delete the error log file
    move %TEMPLOG_SUCCESS% %SUCCESS_LOGDIR%\%FILENAME%
    del %TEMPLOG_ERROR%
)
