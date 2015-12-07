
from paraview.simple import *

from fabric.api import (env, run, cd, get, hide, settings,
                        remote_tunnel, show, shell_env)
from fabric.tasks import execute
from multiprocessing import Process, Value
import traceback
import sys
import multiprocessing as mp
# from multiprocessing import Process, Value

import logging
log = logging.getLogger("paramiko.transport")
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
log.addHandler(sh)


process_id = None
use_multiprocess = True
# Uncomment for output logging
# logger = mp.get_logger()
# logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(mp.SUBDEBUG)
remote_data = True
data_dir = 'data'
data_host = 'user@server'
remote_server_auto = True
paraview_cmd = 'mpiexec pvserver'
paraview_home = '/usr/local/bin/'
job_queue = 'default'
job_tasks = 1
job_ntaskpernode = 1
job_project = 'default'

# If using pvpython stdin is replaced so need to overide
sys.stdin = sys.__stdin__


def pvserver(remote_dir, paraview_cmd, paraview_port, paraview_remote_port):

    with show('debug'), \
         remote_tunnel(int(paraview_remote_port),
                       local_port=int(paraview_port)), cd(remote_dir):
        # with cd(remote_dir):
        if not use_multiprocess:
            run('sleep 2;'+paraview_cmd+'</dev/null &>/dev/null&', pty=False)
        else:
            #    # run('sleep 2;'+paraview_cmd+'&>/dev/null',pty=False)
            run('sleep 2;'+paraview_cmd)  # , pty=False)
        # run(paraview_cmd+'</dev/null &>/dev/null',pty=False)


def pvcluster(remote_dir, paraview_home, paraview_args,
              paraview_port, paraview_remote_port, job_dict):

    with show('debug'), \
         remote_tunnel(int(paraview_remote_port),
                       local_port=int(paraview_port)):
        with shell_env(PARAVIEW_HOME=paraview_home,
                       PARAVIEW_ARGS=paraview_args):
            run('echo $PARAVIEW_HOME')
            run('echo $PARAVIEW_ARGS')
            run('mkdir -p '+remote_dir)
            with cd(remote_dir):
                cmd_line = 'mycluster --create pvserver.job --jobname=pvserver'
                cmd_line += ' --jobqueue ' + job_dict['job_queue']
                cmd_line += ' --ntasks ' + job_dict['job_ntasks']
                cmd_line += ' --taskpernode ' + job_dict['job_ntaskpernode']
                if 'vizstack' in paraview_args:
                    cmd_line += ' --script mycluster-viz-paraview.bsh'
                else:
                    cmd_line += ' --script mycluster-paraview.bsh'
                cmd_line += ' --project ' + job_dict['job_project']
                run(cmd_line)
                run('chmod u+rx pvserver.job')
                run('mycluster --immediate --submit pvserver.job')


def port_test(rport, lport):
    # Run a test
    with hide('everything'), remote_tunnel(int(rport), local_port=int(lport)):
        run('cd')


def run_uname(with_tunnel):

    with hide('everything'):
        run('uname -a')


def test_ssh(status, **kwargs):
    global data_host
    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']
    try:
        env.use_ssh_config = True
        execute(run_uname, False, hosts=[_remote_host])
    except:
        status.value = 0
        return False
    return True


def test_ssh_mp(**kwargs):

    # print 'Starting test ssh'
    status = Value('i', 1)
    process_id = mp.Process(target=test_ssh, args=(status,), kwargs=kwargs)
    process_id.start()
    process_id.join()
    if status.value == 0:
        return False

    return True


def test_remote_tunnel(**kwargs):
    global data_host

    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']

    try:
        env.use_ssh_config = True
        execute(run_uname, True, hosts=[_remote_host])
    except:
        return False

    return True


def get_remote_port(**kwargs):

    global data_host, paraview_remote_port, paraview_port

    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']

    paraview_port = '11111'
    if 'paraview_port' in kwargs:
        paraview_port = kwargs['paraview_port']

    paraview_remote_port = '11113'
    if 'paraview_remote_port' in kwargs:
        paraview_remote_port = kwargs['paraview_remote_port']
    else:
        # Attempt to find an unused remote port
        print 'Attempting to find unused port'
        for p in range(12000, 13000):
            tp = Value('i', p)

            process_id = mp.Process(target=test_remote_port,
                                    args=(port_test, tp,
                                          paraview_port, _remote_host))
            process_id.start()
            process_id.join()
            # print tp.value
            if tp.value != 0:
                break

        print 'Selected Port: '+str(p)
        paraview_remote_port = p


def test_remote_port(port_test, port, paraview_port, remote_host):

    try:
        env.use_ssh_config = True
        execute(port_test, port.value, paraview_port, hosts=[remote_host])
        return True
    except:
        port.value = 0
        return False


def pvserver_start(remote_host, remote_dir, paraview_cmd):
    if paraview_cmd is not None:
        env.use_ssh_config = True
        execute(pvserver, remote_dir, paraview_cmd, hosts=[remote_host])


def pvserver_connect(**kwargs):
    """
    Be careful when adding to this function fabric execute calls do not play
    well with multiprocessing. Do not mix direct fabric execute call and
    mp based fabric execute calls
    """
    global remote_data, data_dir, data_host, remote_server_auto
    global paraview_cmd, process_id, paraview_port, paraview_remote_port
    global process_id

    _paraview_cmd = paraview_cmd
    if 'paraview_cmd' in kwargs:
        _paraview_cmd = kwargs['paraview_cmd']

    if '-sp' in _paraview_cmd or '--client-host' in _paraview_cmd:
        print('pvserver_process: Please only provide pvserver'
              'executable path and name without arguments')
        print 'e.g. mpiexec -n 1 /path_to_pvserver/bin/pvserver'
        return False

    # Add Check for passwordless ssh
    print 'Testing passwordless ssh access'
    if not test_ssh_mp(**kwargs):
        print 'ERROR: Passwordless ssh access to data host failed'
        return False
    print '-> Passed'

    # Add check for paraview version

    # Find free remote port
    get_remote_port(**kwargs)

    paraview_port = '11111'
    if 'paraview_port' in kwargs:
        paraview_port = kwargs['paraview_port']

    if not use_multiprocess:
        pvserver_process(**kwargs)
    else:
        print 'Starting pvserver connect'
        process_id = mp.Process(target=pvserver_process, kwargs=kwargs)
        process_id.start()
        # process_id.join()

    # time.sleep(6)

    ReverseConnect(paraview_port)

    return True


def pvcluster_process(**kwargs):
    pvserver_process(**kwargs)


def pvserver_process(**kwargs):

    global remote_data, data_dir, data_host, remote_server_auto
    global paraview_cmd, paraview_home, paraview_port, paraview_remote_port

    print 'Starting pvserver process'

    _remote_dir = data_dir
    if 'data_dir' in kwargs:
        _remote_dir = kwargs['data_dir']
    _paraview_cmd = paraview_cmd
    if 'paraview_cmd' in kwargs:
        _paraview_cmd = kwargs['paraview_cmd']
    _paraview_home = paraview_home
    if 'paraview_home' in kwargs:
        _paraview_home = kwargs['paraview_home']
    paraview_port = '11111'
    if 'paraview_port' in kwargs:
        paraview_port = kwargs['paraview_port']

    """
    _job_ntasks = 1
    if 'job_ntasks' in kwargs:
        _job_ntasks = kwargs['job_ntasks']
    """

    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']

    # This global variable may have already been set so check
    if 'paraview_remote_port' not in globals():
        paraview_remote_port = '11113'
        if 'paraview_remote_port' in kwargs:
            paraview_remote_port = kwargs['paraview_remote_port']
        else:
            # Attempt to find an unused remote port
            print 'Attempting to find unused port'
            for p in range(12000, 13000):
                print "Trying port: "+str(p)+' '+_remote_host
                try:
                    env.use_ssh_config = True
                    execute(port_test, int(p), int(paraview_port),
                            hosts=[_remote_host])
                    break
                except Exception, e:
                    print 'port_test exception: '+str(e)
                    traceback.print_exc(file=sys.stdout)
                    pass
            print 'Selected Port: '+str(p)
            paraview_remote_port = p

    if 'job_queue' in kwargs:
        # Submit job

        remote_hostname = _remote_host[_remote_host.find('@')+1:]

        if 'vizstack' in kwargs:
            paraview_args = ('/opt/vizstack/bin/viz-paraview -r ' +
                             str(kwargs['job_ntasks']) + ' -c ' +
                             remote_hostname + ' -p ' +
                             str(paraview_remote_port))
        else:
            paraview_args = (' -rc --client-host=' + remote_hostname +
                             ' -sp=' + str(paraview_remote_port))

        print paraview_args

        job_dict = {
            'job_queue': kwargs['job_queue'],
            'job_ntasks': kwargs['job_ntasks'],
            'job_ntaskpernode': kwargs['job_ntaskpernode'],
            'job_project': kwargs['job_project'],
        }
        if _paraview_home is not None:
            env.use_ssh_config = True
            execute(pvcluster, _remote_dir, _paraview_home, paraview_args,
                    paraview_port, paraview_remote_port,
                    job_dict, hosts=[_remote_host])
    else:
        # Run Paraview
        if '-sp' in _paraview_cmd or '--client-host' in _paraview_cmd:
            print ('pvserver_process: Please only provide pvserver'
                   'executable path and name without arguments')
            print 'e.g. mpiexec -n 1 /path_to_pvserver/bin/pvserver'
            return False
        if 'vizstack' in kwargs:
            _paraview_cmd = (_paraview_cmd + ' -c localhost ' + ' -p ' +
                             str(paraview_remote_port))
        else:
            _paraview_cmd = (_paraview_cmd +
                             ' -rc --client-host=localhost -sp=' +
                             str(paraview_remote_port))

        if _paraview_cmd is not None:
            env.use_ssh_config = True
            execute(pvserver, _remote_dir, _paraview_cmd, paraview_port,
                    paraview_remote_port, hosts=[_remote_host])


def pvserver_disconnect():
    Disconnect()
    if process_id:
        process_id.terminate()
