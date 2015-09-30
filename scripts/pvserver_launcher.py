#!/usr/bin/env python

import sys
from pvconnect import pvserver_process

if len(sys.argv) < 5:
    print 'Incorrect usage'
    print ('pververlauncher.py server_port user@host' +
           ' remote_paraview_location mpi_num_tasks')
    sys.exit(0)

data_host = sys.argv[2]
data_dir = '.'
job_ntasks = sys.argv[4]
paraview_cmd = 'mpiexec -n ' + str(job_ntasks) + ' ' + sys.argv[3]+'/pvserver'

pvserver_process(data_host=data_host,
                 data_dir=data_dir,
                 paraview_cmd=paraview_cmd,
                 job_ntasks=job_ntasks)
