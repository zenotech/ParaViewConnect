#!/usr/bin/env python

import sys
import uuid
from pvconnect import pvcluster_process

if len(sys.argv) < 8:
    print 'Incorrect usage'
    print ('pververlauncher.py server_port user@host' +
           ' remote_paraview_location job_queue ' +
           'mpi_num_tasks job_ntask_per_node job_project' +
           ' mpiexec (optional)' +
           ' shell prefix command (optional)')
    sys.exit(0)

data_host = sys.argv[2]
data_dir = '~/.zpost/' + str(uuid.uuid4())
paraview_home = sys.argv[3]
job_queue = sys.argv[4]
job_ntasks = sys.argv[5]
job_ntaskpernode = sys.argv[6]
job_project = sys.argv[7]


mpiexec = 'mpiexec'
if len(sys.argv) > 8:
    mpiexec = sys.argv[8]
shell_cmd = ''
if len(sys.argv) > 9:
    for i in range(9, len(sys.argv)):
        shell_cmd += sys.argv[i] + ' '

paraview_cmd = (shell_cmd +
                mpiexec + ' -n ' +
                str(job_ntasks) +
                ' ' +
                paraview_home +
                '/pvserver')

pvcluster_process(data_host=data_host,
                  data_dir=data_dir,
                  paraview_cmd=paraview_cmd,
                  job_queue=job_queue,
                  job_ntasks=job_ntasks,
                  job_ntaskpernode=job_ntaskpernode,
                  job_project=job_project)
