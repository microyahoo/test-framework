#! /usr/bin/env python

import json
import os
import select
import shlex
import subprocess
import IssueCmd

XMS_CLI_USER = os.environ.get("ENV_XMS_CLI_USER", "admin")
XMS_CLI_PWD = os.environ.get("ENV_XMS_CLI_PWD", "admin")
XMS_REST_PORT = os.environ.get("ENV_XMS_REST_PORT", 8056)

XMS_CLI_HEADER = "xms-cli --user {user} --password {pwd} ".format(user=XMS_CLI_USER, pwd=XMS_CLI_PWD)

XMS_REST_BASE_URL = "http://{ip}:%s/v1/" % (XMS_REST_PORT)
XMS_CURL_POST_HEADER = "curl -H \"Content-Type:application/json\" -X POST --data \'{data}\' "
XMS_CURL_GET_HEADER = "curl -H \"Content-Type:application/json\" -X GET "

token_parameter = {
    "auth": {
        "identity": {
            "password": {
                "user": {
                    "name": XMS_CLI_USER,
                    "password": XMS_CLI_PWD
                }
            }
        }
    }
}

def get_access_token(host="localhost"):
    retval = -1
    url = XMS_REST_BASE_URL.format(ip=host) + "auth/tokens" 
    curl_header = XMS_CURL_POST_HEADER.format(data=json.dumps(token_parameter))
    cmd = curl_header + url
    # print cmd
    ret = execute_cmd_in_host(cmd, host)
    if ret[2] == 0:
        try:
            return json.loads(ret[0])['token']['uuid']
        except Exception as e:
            print("[Error] The format of access token data is invalid. Error\
                  message: " + e.message)
    return retval

def execute_cmd_in_host(cmd, host=None):
    """
    args:
        cmd:  command
        host: the command runs in specified host. The default value is None, which stands for in local.
    """
    if host:
        ret = IssueCmd.issue_cmd_via_root(cmd, host)
    else:
        rc, stdout, stderr = run_command(cmd)
        ret = [stdout, stderr, rc] 
    return ret

# the following code logic is taken from ansible source code
def run_command(cmd, environ_update=None, cwd=None, umask=None):
    # print environ_update
 
    args = shlex.split(cmd)
    args = [os.path.expanduser(os.path.expandvars(x)) for x in args if x is not None]
    # print args

    rc = 0

    # Manipulate the environ we'll send to the new process
    old_env_vals = {}
    if environ_update:
        for key, val in environ_update.items():
            old_env_vals[key] = os.environ.get(key, None)
            os.environ[key] = val

    kwargs = dict(
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
    )
    # store the pwd
    prev_dir = os.getcwd()

    # make sure we're in the right working directory
    if cwd and os.path.isdir(cwd):
        cwd = os.path.abspath(os.path.expanduser(cwd))
        kwargs['cwd'] = cwd
        try:
            os.chdir(cwd)
        except (OSError, IOError) as e:
            print(e)
            # self.fail_json(rc=e.errno, msg="Could not open %s, %s" % (cwd, to_native(e)),
            #                exception=traceback.format_exc())

    old_umask = None
    if umask:
        old_umask = os.umask(umask)

    try:
        stdout = ''
        stderr = ''

        cmd = subprocess.Popen(args, **kwargs)

        rpipes = [cmd.stdout, cmd.stderr]

        while True:
            rfds, wfds, efds = select.select(rpipes, [], rpipes, 1)
            stdout += _read_from_pipes(rpipes, rfds, cmd.stdout)
            stderr += _read_from_pipes(rpipes, rfds, cmd.stderr)
            # only break out if no pipes are left to read or
            # the pipes are completely read and
            # the process is terminated
            if (not rpipes or not rfds) and cmd.poll() is not None:
                break
            # No pipes are left to read but process is not yet terminated
            # Only then it is safe to wait for the process to be finished
            # NOTE: Actually cmd.poll() is always None here if rpipes is empty
            elif not rpipes and cmd.poll() is None:
                cmd.wait()
                # The process is terminated. Since no pipes to read from are
                # left, there is no need to call select() again.
                break
        cmd.stdout.close()
        cmd.stderr.close()

        rc = cmd.returncode
    except Exception as e:
        rc = -1
        print(e)

    # Restore env settings
    for key, val in old_env_vals.items():
        if val is None:
            del os.environ[key]
        else:
            os.environ[key] = val

    if old_umask:
        os.umask(old_umask)

    # reset the pwd
    os.chdir(prev_dir)

    return (rc, stdout, stderr)

def _read_from_pipes(rpipes, rfds, file_descriptor):
    data = ''
    if file_descriptor in rfds:
        data = os.read(file_descriptor.fileno(), 9000)
        if data == '':
            rpipes.remove(file_descriptor)

    return data

if __name__ == "__main__":
    host = "10.0.11.233"
    print(get_access_token(host))
