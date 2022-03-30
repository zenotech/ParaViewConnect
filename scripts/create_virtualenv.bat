@ECHO OFF

echo "ParaViewConnect installer"


if exist "./pvconnect-py3/" rd /q /s "./pvconnect-py3/"

echo "Creating virtual environment"
py -m venv pvconnect-py3
IF %ERRORLEVEL% == 0 GOTO VirtualEnvCreated
ECHO virtualenv could not be created
GOTO EOF
:VirtualEnvCreated


echo "Activating virtual environment"
call pvconnect-py3\scripts\activate

echo "Installing requirements"
pip install -r requirements.txt 

deactivate

popd
popd

:EOF
