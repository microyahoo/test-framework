#! /usr/bin/env python

import json
import utils

def get_host_id(host_name, host=None):
    """
    return the block volume id according to the volume name.
    """
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f json host list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or isinstance(ret[0], dict):
        print "[Error] Failed to get host info. Error message: [{err}]".format(err=ret[1])
        return retval
    try:
        host_info = json.loads(ret[0])
        hosts = host_info["hosts"]
        for h in hosts:
            if host_name == h["name"]:
                return h["id"]
    except Exception as e:
        print "[Error] error message is: " + e.message
    return retval

