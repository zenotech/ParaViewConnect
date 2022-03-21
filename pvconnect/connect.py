

from fabric import Connection
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
job_queue = 'default'
job_tasks = 1
job_ntaskpernode = 1
job_project = 'default'

# If using pvpython stdin is replaced so need to overide
sys.stdin = sys.__stdin__
sys.stdout = sys.__stdout__


def pvserver(conn, remote_dir, paraview_cmd, paraview_port, paraview_remote_port):

    with conn.forward_remote(remote_port=int(paraview_remote_port), local_port=int(paraview_port)):
        conn.cd(remote_dir)
        if not use_multiprocess:
            conn.run('sleep 2;' + paraview_cmd +
                '</dev/null &>/dev/null&', pty=False)
        else:
            #    # run('sleep 2;'+paraview_cmd+'&>/dev/null',pty=False)
            conn.run('sleep 2;' + paraview_cmd)  # , pty=False)
        # run(paraview_cmd+'</dev/null &>/dev/null',pty=False)

def pvcluster(conn, remote_dir, paraview_cmd, paraview_args,
              paraview_port, paraview_remote_port, job_dict,
              shell_cmd):
    with conn.forward_remote(remote_port=int(paraview_remote_port), local_port=int(paraview_port)):
        env = { 'PARAVIEW_CMD':paraview_cmd,
                'PARAVIEW_ARGS':paraview_args}
        conn.run('echo $PARAVIEW_HOME', env=env)
        conn.run('echo $PARAVIEW_ARGS', env=env)
        conn.run('mkdir -p ' + remote_dir)
        with conn.cd(remote_dir):
            cmd_line = shell_cmd
            cmd_line += 'mycluster --create pvserver.job --jobname=pvserver'
            cmd_line += ' --jobqueue ' + job_dict['job_queue']
            cmd_line += ' --ntasks ' + job_dict['job_ntasks']
            cmd_line += ' --taskpernode ' + job_dict['job_ntaskpernode']
            if 'vizstack' in paraview_args:
                cmd_line += ' --script mycluster-viz-paraview.bsh'
            else:
                cmd_line += ' --script mycluster-paraview.bsh'
            cmd_line += ' --project ' + job_dict['job_project']
            conn.run(cmd_line, env=env)
            conn.run('chmod u+rx pvserver.job')
            conn.run(shell_cmd+'mycluster --immediate --submit pvserver.job', env=env)


def port_test(conn, rport, lport):
    # Run a test
    with conn.forward_remote(remote_port=int(rport), local_port=int(lport)):
        conn.run('cd', hide=True)

def run_uname(conn):
   conn.run('uname -a', timeout=5, hide=True)


def test_ssh(status, **kwargs):
    global data_host
    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']
    try:
        con = Connection(host=_remote_host)
        run_uname(con)
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
        conn = Connection(host=_remote_host)
        run_uname(conn)
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
        print('Attempting to find unused port')
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

        print('Selected Port: ' + str(p))
        paraview_remote_port = p


def test_remote_port(port_test, port, paraview_port, remote_host):

    try:
        conn = Connection(host=remote_host)
        port_test(conn, port.value, paraview_port)
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
        print('e.g. mpiexec -n 1 /path_to_pvserver/bin/pvserver')
        return False

    # Add Check for passwordless ssh
    print('Testing passwordless ssh access')
    if not test_ssh(status=Value('i', 1),**kwargs):
        print('ERROR: Passwordless ssh access to data host failed')
        return False
    print('-> Passed')

    # Add check for paraview version

    # Find free remote port
    get_remote_port(**kwargs)

    paraview_port = '11111'
    if 'paraview_port' in kwargs:
        paraview_port = kwargs['paraview_port']

    if not use_multiprocess:
        pvserver_process(**kwargs)
    else:
        print('Starting pvserver connect')
        process_id = mp.Process(target=pvserver_process, kwargs=kwargs)
        process_id.start()
        # process_id.join()

    # time.sleep(6)

    # ReverseConnect(paraview_port)

    return True


def pvcluster_process(**kwargs):
    pvserver_process(**kwargs)


def pvserver_process(**kwargs):

    global remote_data, data_dir, data_host, remote_server_auto
    global paraview_cmd, paraview_port, paraview_remote_port

    print('Starting pvserver process')

    _remote_dir = data_dir
    if 'data_dir' in kwargs:
        _remote_dir = kwargs['data_dir']
    _paraview_cmd = paraview_cmd
    if 'paraview_cmd' in kwargs:
        _paraview_cmd = kwargs['paraview_cmd']
    paraview_port = '11111'
    if 'paraview_port' in kwargs:
        paraview_port = kwargs['paraview_port']
    shell_cmd = ''
    if 'shell_cmd' in kwargs:
        shell_cmd = kwargs['shell_cmd']
    if 'remote_hostname' in kwargs:
        remote_hostname = kwargs['remote_hostname']

    """
    _job_ntasks = 1
    if 'job_ntasks' in kwargs:
        _job_ntasks = kwargs['job_ntasks']
    """

    _remote_host = data_host
    if 'data_host' in kwargs:
        _remote_host = kwargs['data_host']

    print ("Remote host %s" % _remote_host)

    print('Testing passwordless ssh access')
    try:
        conn = Connection(host=_remote_host)
        run_uname(conn)
        print('SSH OK')
    except Exception as e:
        print ('ERROR: Passwordless ssh access to data host' +
               'failed: %s' % str(e))
        sys.exit(0)

    # This global variable may have already been set so check
    if 'paraview_remote_port' not in globals():
        paraview_remote_port = '11113'
        if 'paraview_remote_port' in kwargs:
            paraview_remote_port = kwargs['paraview_remote_port']
        else:
            # Attempt to find an unused remote port
            print('Attempting to find unused port')
            for p in range(12000, 13000):
                print("Trying port: " + str(p) + ' ' + _remote_host)
                try:
                    conn = Connection(host=_remote_host)
                    port_test(conn,  int(p), int(paraview_port))
                    break
                except Exception as e:
                    print('port_test exception: ' + str(e))
                    traceback.print_exc(file=sys.stdout)
                    pass
            print('Selected Port: ' + str(p))
            paraview_remote_port = p

    if 'job_queue' in kwargs:
        # Submit job

        if not remote_hostname or len(remote_hostname) == 0:
            remote_hostname = _remote_host[_remote_host.find('@') + 1:]

        if 'vizstack' in kwargs:
            paraview_args = ('/opt/vizstack/bin/viz-paraview -r ' +
                             str(kwargs['job_ntasks']) + ' -c ' +
                             remote_hostname + ' -p ' +
                             str(paraview_remote_port))
        else:
            paraview_args = (' -rc --client-host=' + remote_hostname +
                             ' -sp=' + str(paraview_remote_port))

        print(paraview_args)

        job_dict = {
            'job_queue': kwargs['job_queue'],
            'job_ntasks': kwargs['job_ntasks'],
            'job_ntaskpernode': kwargs['job_ntaskpernode'],
            'job_project': kwargs['job_project'],
        }
        if _paraview_cmd is not None:
            conn = Connection(host=_remote_host)
            pvcluster(conn, _remote_dir, _paraview_cmd, paraview_args,
                    paraview_port, paraview_remote_port,
                    job_dict, shell_cmd)
    else:
        # Run Paraview
        if '-sp' in _paraview_cmd or '--client-host' in _paraview_cmd:
            print ('pvserver_process: Please only provide pvserver'
                   'executable path and name without arguments')
            print('e.g. mpiexec -n 1 /path_to_pvserver/bin/pvserver')
            return False
        if 'vizstack' in kwargs:
            _paraview_cmd = (_paraview_cmd + ' -c localhost ' + ' -p ' +
                             str(paraview_remote_port))
        else:
            _paraview_cmd = (_paraview_cmd +
                             ' -rc --client-host=localhost -sp=' +
                             str(paraview_remote_port))

        if _paraview_cmd is not None:
            conn = Connection(host=_remote_host)
            pvserver(conn, _remote_dir, _paraview_cmd, paraview_port,
                    paraview_remote_port)


def pvserver_disconnect():
    #Disconnect()
    if process_id:
        process_id.terminate()
