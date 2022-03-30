@ECHO OFF

echo "ParaViewConnect installer"


if exist "./pvconnect-py27/" rd /q /s "./pvconnect-py27/"

echo "Creating virtual environment"
py -m venv pvconnect-py27
IF %ERRORLEVEL% == 0 GOTO VirtualEnvCreated
ECHO virtualenv could not be created
GOTO EOF
:VirtualEnvCreated


echo "Activating virtual environment"
call pvconnect-py27\scripts\activate

echo "Installing requirements"
pip install -r requirements.txt 

deactivate

popd
popd

:EOF
