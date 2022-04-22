pushd "%~dp0" 

echo "Activating virtual environment"
call ..\pvconnect-py3\scripts\activate

set PYTHONPATH=%cd%\..
echo %PYTHONPATH%

python pvcluster_launcher.py %* 
