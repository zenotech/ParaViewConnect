# ParaViewConnect
Python3 library and command line tool to help starting and connecting to remote Linux ParaView servers. It sets up the required ssh tunnels to establish a forward or reverse connection to a remote host and launches the paraview pvserver process. 
The client supports Windows, MacOS and Linux but is designed to connect to Linux based remote servers. 
For the current release of ParaviewConnect, Windows users are recommneded to use [[WSL](https://learn.microsoft.com/en-us/windows/wsl/install)].
___
## Requirements
1. Your local machine has python with the latest version of pip installed
2. Your local machine and remote server have matching versions of paraview and paraview server installed, and you know the location of the Paraview Server binary (pvserver) on the remote host. See below for application specific configuration tips.
>       Currently zCFD is using paraview 5.10
3. You have [passwordless ssh](https://www.redhat.com/sysadmin/passwordless-ssh) set up to the remote server, allowing you to connect to the remote host without entering a password
___
## Installation

### From PyPi
You can install the package from PyPi using pip with `pip install paraview-connect`

### From Github
You can install directly from Github using pip with `pip install git+https://github.com/zenotech/ParaViewConnect.git`

#### MacOS
If installation fails with errors installing/building the cyptography package, please ensure you are using the latest release of pip.

___

## Configuration
Configure paraview-connect by running `paraview-connect configure`. This will then prompt you to enter details of your first connection and save it with a profile name. All confiuration is stored in ~/.paraview-connect/config by default. You will be presented with the following prompts, values in brackets are shown as the default entries. This example will set up a connection to `joe.blogs@login1.server.com`

```
Paraview Connect
----------------
Configuring Paraview Connect
Hostname or IP to connect to: login1.server.com
Username on remote system: joe.blogs
Certificate to connect with [~/.ssh/id_rsa]:
Is cerfiticate passphrase protected? [y/N]:
Local port to use for connection [11111]:
Number of MPI processes to use [1]:
Paraview server command [pvserver]:
Pre script to run before paraview server [None]:
Name of profile to store config as: myFirstConfiguration
```

If you want to add another connection or update the existing one simply run `paraview-connect configure` again. You can store multiple profiles in the configuration file.

### Using .ssh/config files
By default Paraview-connect does not read any of the settings in an ssh config file. If you want to enable this then set the value of `load_ssh_configs` to True in `~/.paraview-connect/config`.
___
## Configuration for zCFD

When configuring for zCFD you can use the paraview-connect to run the zCFD activate script to prepare your remote environment. To do this add it as a pre-script. For example if zCFD was installed in /apps/zcfd/zCFD-icc-sse-impi-2020.12.116-Linux-64bit/ then your pre-sript would be `. /apps/zcfd/zCFD-icc-sse-impi-2020.12.116-Linux-64bit/bin/activate`. Your pvserver command would then just be `pvserver`.

## Configuration for OpenFoam

When configuring for OpenFoam you can use the paraview-connect to source the OpenFoam environment script to prepare your remote environment. To do this add it as a pre-script. For example if OpenFoam was installed in /apps/OpenFoam/OpenFoam-v1806/ then your pre-sript would be `. /apps/OpenFoam/OpenFoam-v1806/etc/bashrc`. 

___
## Usage

To launch paraview connect to use a profile created with `paraview-connect configure` simply run `paraview-connect run <profile-name>`. This will launch the client with the configuration specified for that profile. From within Paraview you can then File->Connect and add/load a server configration connection. The server configration should always connect to your localmachine (localhost) but the port and connection type will depend on your paraview-connection configuration.

The following fields are what are typically required for a paraview-connect connection from within the local paraview client.

| Field       | Value                |
| ----------- | -------------------- |
| Name        | myFirstConfiguration |
| Server Type | Client/ Server       |
| Host        | localhost            |
| Port        | 11111                |

You can also launch sessions directly without using a config file if you run `paraview-connect connect`. Check the command help for the list of switches.
___ 
## Settings
The following settings are defined in the ~/.paraview-connect/config file created by configure. Any settings in the DEFAULT section can be overridden in each profile section if required. 

| Setting           | Description                                                                                                             | Default       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------- |
| cert              | Location of your SSH private key                                                                                        | ./.ssh/id_rsa |
| remote_host       | Hostname or IP or remote machine to connect to                                                                          |               |
| username          | Username to connect with                                                                                                |               |
| pvserver_command  | Name of pvserver binary to launch                                                                                       | pvserver      |
| pre_script        | Custom script to setup env before launching pvserer                                                                     | None          |
| direction         | Type of Paraview Server connection, reverse or forward                                                                  | forward       |
| cluster           | Launch pvserver onto a batch cluster                                                                                    | False         |
| local_port        | Port on localmachine to create connections on                                                                           | 11111         |
| remote_port_range | Paraview-connect will search for an unused port on the remote machine to use, this is the range it checks               | 12000:13000   |
| nprocs            | How many MPI processes to launch paraview with. For values > 1 mpiexec must be available on the remote host.            | 1             |
| load_ssh_configs  | Make use of any local ssh configuration files. If false then the only private key that will be tried is defined as cert | False         |
