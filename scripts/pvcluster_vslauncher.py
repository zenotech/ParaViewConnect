#!/usr/bin/env python

import sys
import uuid

data_host=sys.argv[2]
data_dir='~/.zpost/'+str(uuid.uuid4())
paraview_home=sys.argv[3]
job_queue=sys.argv[4]
job_ntasks=sys.argv[5]
job_ntaskpernode=sys.argv[6]
job_project=sys.argv[7]

from zutil.post import pvcluster_process

pvcluster_process(data_host=data_host,data_dir=data_dir,paraview_home=paraview_home,
                  job_queue=job_queue,job_ntasks=job_ntasks,job_ntaskpernode=job_ntaskpernode,
                  job_project=job_project,vistack=True
                 )
