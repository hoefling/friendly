echo off
REM Default is Python 3.9

if "%1"=="3.6" goto py_36
if "%1"=="3.7" goto py_37
if "%1"=="3.8" goto py_38
if "%1"=="3.9" goto py_39
if "%1"=="3.10" goto py_310
if "%1"=="ipython" goto ipython
if "%1"=="ptk" goto ptk

:py_39
venv-friendly-3.9\scripts\activate
goto end

:py_38
venv-friendly-3.8\scripts\activate
goto end

:py_36
venv-friendly-3.6\scripts\activate
goto end

:py_37
venv-friendly-3.7\scripts\activate
goto end

:py_310
venv-friendly-3.10\scripts\activate
goto end

:ipython
venv-friendly-ipython\scripts\activate
goto end

:ptk
venv-ptk\scripts\activate
goto end



:end
