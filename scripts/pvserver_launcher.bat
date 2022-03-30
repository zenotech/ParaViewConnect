pushd "%~dp0" 

echo "Activating virtual environment"
call ..\pvconnect-py27\scripts\activate

set PYTHONPATH=%cd%\..

echo %PYTHONPATH%

python pvserver_launcher.py %* 
