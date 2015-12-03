@ECHO OFF

echo "ParaViewConnect installer"

IF NOT "%1"=="" GOTO ArgOk
echo "Supply full path for paraview executables" 
goto EOF

:ArgOk

echo "Using ParaView from: %*\pvpython.exe"

pushd "%~dp0"
pushd ..

echo "Checking for pvpython.exe"

IF EXIST "%*\pvpython.exe" goto PVpythonOK
echo "ERROR: pvpython not found"
goto EOF

:PVpythonOK
echo "Using %*\pvpython.exe"

echo "Checking for virtualenv"

REM Check for virtualenv
WHERE virtualenv --version 2>NUL
IF %ERRORLEVEL% == 0 GOTO VirtualEnvOK
ECHO virtualenv not found
GOTO EOF

:VirtualEnvOK

if exist "./pvconnect-py27/" rd /q /s "./pvconnect-py27/"

echo "Creating virtual environment"
virtualenv pvconnect-py27
IF %ERRORLEVEL% == 0 GOTO VirtualEnvCreated
ECHO virtualenv could not be created
GOTO EOF
:VirtualEnvCreated


echo "Activating virtual environment"
call pvconnect-py27\scripts\activate

echo "Installing yolk"
pip install yolk

echo "Installing requirements"
pip install -r requirements.txt 

yolk -l

echo "Saving Paraview location info"
echo SET PARAVIEW_BIN_LOCATION=%*> pvconnect-py27\pv-location.bat

deactivate

popd
popd

:EOF