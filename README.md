# ParaViewConnect
Python library to help starting and connecting to remote ParaView servers

## Installation instructions:

### All operating systems:
1. Ensure you have Python (including virtualenv package) and paraview installed.
2. Ensure you have [keyless ssh](https://www.redhat.com/sysadmin/passwordless-ssh) access set up with the cluster you intend to interact with, and create a config file in ~/.ssh/config pointing to your openSSH key.

Example:
```
Host login1
    Hostname login1
    User joe.blogs
    IdentityFile ~/.ssh/id_rsa
```

### Linux
3. Clone this repository to your local machine
4. From the **scripts** folder run 

> ./create_virtualenv.bsh /path/to/ParaView/bin/pvpython

5. Launch paraview and load servers from `./share/servers.pvsc`
6. When connecting set "launcher location" to be the `scripts` folder of this package

### Windows
3. Clone this repository to your local machine
4. From **repository root** folder run:
> `.\scripts\create_virtualenv.bat 

5. Launch paraview and load servers from `.\share\servers-windows.pvsc` 
6. When connecting set "launcher location" to be the repository root folder of this package. (`c:\PATH\TO\ParaviewConnect`)

### Mac
3. From the location you want paraview connect to be installed to run:
> brew install openssl rust
LDFLAGS="-L$(brew --prefix openssl@1.1)/lib" CFLAGS="-I$(brew --prefix openssl@1.1)/include" ./create_virtualenv.bsh /Applications/ParaView-5.9.0.app/Contents/bin/pvpython

4. Launch paraview and load servers from `./share/servers.pvsc`
5. When connecting set "launcher location" to be the `scripts` folder of this package

Paraview Client
---------------

This library can also be used to simplify the launching of a pvserver from the ParaView client. The launcher scripts setup a secure reverse connection from the ParaView server using an automatically discovered unused port in the range of 12000-13000.

For an example ParaView server config file see shared/servers.pvsc

The launcher scripts are in scripts/pvserver_launcher.bsh and scripts/pvcluster_launcher.bsh

This relies on passwordless ssh key based authentication on the remote server so ensure this works correctly before using this facility.

Server Dependencies
-------------------

The server environment requires the MyCluster application to the installed and configured correctly for the cluster capability to operate.
The server submit node also requires that the ssh server is configured to act as a gateway so that the cluster nodes can connect to the ParaView client. 

These options need to be set in the /etc/ssh/sshd_config file on the server

AllowTcpForwarding yes

GatewayPorts yes 

To use the cluster capabilities from python instead of calling

> pvserver_connect(data_host=data_host,data_dir=data_dir,paraview_cmd=paraview_cmd)

Use

> pvserver_connect(data_host=data_host,data_dir=data_dir,paraview_cmd=paraview_cmd,job_queue=your_job_queue,
job_ntasks=your_number_of_mpi_tasks,job_ntaskpernode=your_number_of_tasks_per_node,job_project=your_job_project)

