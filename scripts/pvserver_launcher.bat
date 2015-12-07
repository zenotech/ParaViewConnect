pushd "%~dp0" 

echo "Activating virtual environment"
call ..\pvconnect-py27\scripts\activate

call ..\pvconnect-py27\pv-location.bat

echo "%PARAVIEW_BIN_LOCATION%"
set PATH=%PARAVIEW_BIN_LOCATION%;%PATH%
set PYTHONPATH=..;%PARAVIEW_SITE_LIB%\site-packages;%PARAVIEW_SITE_LIB%\site-packages\vtk;%PYTHONPATH%

echo %PYTHONPATH%

python pvserver_launcher.py %* 