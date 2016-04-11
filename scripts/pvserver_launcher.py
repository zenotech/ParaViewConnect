#!/usr/bin/env python

import sys
from pvconnect import pvserver_process

if len(sys.argv) < 5:
    print 'Incorrect usage'
    print ('pververlauncher.py server_port user@host' +
           ' remote_paraview_location mpi_num_tasks' +
           ' mpiexec (optional)' +
           ' shell prefix command (optional)')
    sys.exit(0)

data_host = sys.argv[2]
data_dir = '.'
remote_location = sys.argv[3]
job_ntasks = sys.argv[4]
mpiexec = 'mpiexec'
if len(sys.argv) > 5:
    mpiexec = sys.argv[5]
shell_cmd = ''
if len(sys.argv) > 6:
    for i in range(6, len(sys.argv)):
        shell_cmd += sys.argv[i] + ' '
paraview_cmd = (shell_cmd +
                mpiexec + ' -n ' +
                str(job_ntasks) +
                ' ' +
                remote_location +
                '/pvserver')

pvserver_process(data_host=data_host,
                 data_dir=data_dir,
                 paraview_cmd=paraview_cmd,
                 job_ntasks=job_ntasks)
