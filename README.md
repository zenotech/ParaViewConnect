# ParaViewConnect
Python3 library and command line tool to help starting and connecting to remote Linux ParaView servers. It sets up the required ssh tunnels to establish a forward or reverse connection to a remote host and launches the paraview pvserver process. 
The client supports Windows, MacOS and Linux but is designed to connect to Linux based remote servers. 

## Installation

### From PyPi
You can install the package from PyPi using pip with `pip install paraview-connect`

### From Github
You can install directly from Github using pip with `pip install git+https://github.com/zenotech/ParaViewConnect.git@develop`

### MacOS
If installation fails with errors installing/building the cyptography package, please ensure you are using the latest release of pip.

## Configuration
Paraview-connect makes use of passwordless ssh connections to the remote host. To do this you will require an account and ssh key that lets you login to the remote host without entering a password.

As well as an ssh key you will also need to know the location of the Paraview Server binary (pvserver) on your remote host, see below for application specific configuration tips.

Once you have a key you can configure paraview-connection by running `paraview-connect configure`. This will then prompt you to enter details of your first connection and save it with a profile name. All confiuration is stored in ~/.paraview-connect/config by default.

If you want to add another connection or update the existing one simply run `paraview-connect configure` again. You can store multiple profiles in the configuration file.

### Using .ssh/config files
By default Paraview-connect does not read any of the settings in an ssh config file. If you want to enable this then set the value of `load_ssh_configs` to True in `~/.paraview-connect/config`.

### Configuration for zCFD

When configuring for zCFD you can use the paraview-connect to run the zCFD activate script to prepare your remote environment. To do this add it as a pre-script. For example if zCFD was installed in /apps/zcfd/zCFD-icc-sse-impi-2020.12.116-Linux-64bit/ then your pre-sript would be `. /apps/zcfd/zCFD-icc-sse-impi-2020.12.116-Linux-64bit/bin/activate`. Your pvserver command would then just be `pvserver`.

### Configuration for OpenFoam

When configuring for OpenFoam you can use the paraview-connect to source the OpenFoam environment script to prepare your remote environment. To do this add it as a pre-script. For example if OpenFoam was installed in /apps/OpenFoam/OpenFoam-v1806/ then your pre-sript would be `. /apps/OpenFoam/OpenFoam-v1806/etc/bashrc`. 

## Usage

To launch paraview connect to use a profile created with `paraview-connect configure` simply run `paraview-connect run <profile-name>`. This will launch the client with the configuration specified for that profile. From within Paraview you can then File->Connect and add/load a server configration connection. The server configration should always connect to your localmachine (localhost) but the port and connection type will depend on your paraview-connection configuration.

You can also launch sessions directly without using a config file if you run `paraview-connect connect`. Check the command help for the list of switches.

## Settings
The following settings are defined in the ~/.paraview-connect/config file created by configure. Any settings in the DEFAULT section can be overridden in each profile section if required. 

| Setting | Description | Default |
| --- | --- | --- |
| cert | Location of your SSH private key  | ./.ssh/id_rsa |
| remote_host | Hostname or IP or remote machine to connect to  | |
| username | Username to connect with  |  |
| pvserver_command | Name of pvserver binary to launch | pvserver |
| pre_script | Custom script to setup env before launching pvserer | None |
| direction | Type of Paraview Server connection, reverse or forward | reverse |
| cluster | Launch pvserver onto a batch cluster | False |
| local_port | Port on localmachine to create connections on | 11111 |
| remote_port_range | Paraview-connect will search for an unused port on the remote machine to use, this is the range it checks | 12000:13000 |
| nprocs | How many MPI processes to launch paraview with. For values > 1 mpiexec must be available on the remote host. | 1 |
| load_ssh_configs | Make use of any local ssh configuration files. If false then the only private key that will be tried is defined as cert | False |
