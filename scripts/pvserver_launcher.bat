pushd "%~dp0" 

echo "Activating virtual environment"
call ..\pvconnect-py27\scripts\activate

call ..\pvconnect-py27\pv-location.bat

echo "%PARAVIEW_BIN_LOCATION%..bin\"
set PATH=%PARAVIEW_BIN_LOCATION%\..\bin;%PATH%
set PYTHONPATH=..;%PARAVIEW_BIN_LOCATION%\..\lib\paraview-4.3\site-packages;%PARAVIEW_BIN_LOCATION%\..\lib\paraview-4.3\site-packages\vtk;%PYTHONPATH%

echo %PYTHONPATH%

python pvserver_launcher.py %* 