# ParaViewConnect
Python library to help starting and connecting to remote ParaView servers

## Installation instructions:

### Linux
Ensure you have Python 2.7 (including virtualenv package) and Paraview installed. 
Note ParaView needs to use the same version of python

In the scripts folder run 

> ./create_virtualenv.bsh /path/to/ParaView/bin/pvpython


If you want to run a custom version of Paraview please set the PARAVIEW_HOME variable in your shell before starting the notebook server

On Centos 6 series install dependencies as root

> curl https://bootstrap.pypa.io/get-pip.py | python -

> pip install virtualenv

> yum groupinstall -y development

> yum install -y zlib-dev openssl-devel sqlite-devel bzip2-devel python-devel libffi-devel

### Windows
Ensure you have Python 2.7, Virtualenv and Paraview installed. You will also need the Microsoft Visual C++ compiler (either an installation of Visual Studio or the Visual C++ Compiler for Python 2.7).
You also need to setup keyless ssh access and create a config file in ~/.ssh/config pointing to your openSSH key.
Example:
```
Host login1
    Hostname login1
    User joe.blogs
    IdentityFile ~/.ssh/id_rsa
```

Follow the following steps to install under Windows  
1. From the scripts folder run "create_virtualenv.bat path-to-paraview-bin"  
2. Launch paraview and load servers from ./share/servers-windows.pvsc  
3. When connecting set "launcher location" to be the location of this package



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

