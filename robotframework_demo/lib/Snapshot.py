#! /usr/bin/env python

import datetime
import time
import uuid
import random
import json
import utils
import BlockVolume

def create_block_snapshot(snapshot_name, block_volume, description=None, host=None):
    retval = 0
    if not isinstance(block_volume, int):
        block_volume = BlockVolume.get_block_volume_id(block_volume, host)
    if block_volume == -1:
        print "[Error] The block volume id is invalid."
        return -1
    if description is None:
        cmd = utils.XMS_CLI_HEADER + "block-snapshot create --block-volume {volume} {snap}".format(volume=block_volume, snap=snapshot_name)
    else:
        cmd = utils.XMS_CLI_HEADER + "block-snapshot create --block-volume {volume} --description {des} {snap}".format(volume=block_volume, snap=snapshot_name, des=description)
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to create block snapshot. Error message: [{err}]".format(err=ret[1])
        retval = -1
    return retval

def delete_block_snapshot(snapshot, host=None):
    retval = 0
    if not isinstance(snapshot, int):
        snapshot = get_block_snapshot_id(snapshot, host)
    if snapshot == -1:
        print "[Error] The block snapshot name/id is invalid."
        return -1
    cmd = utils.XMS_CLI_HEADER + "block-snapshot delete {snapid}".format(snapid=snapshot)
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to delete block snapshot. Error message: [{err}]".format(err=ret[1])
        retval = -1
    return retval

def get_block_snapshot_ids(host=None):
    retval = -1
    ss_list = []
    cmd = utils.XMS_CLI_HEADER + "-f json block-snapshot list"
    # print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get snapshot info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            snapshotinfo = json.loads(ret[0])
            snapshot_list = snapshotinfo["block_snapshots"]
            for s in snapshot_list:
                ss_list.append(s["id"])
            retval = 0
        except Exception as e:
            print "[Error] the error message is: " + e.message
    return retval, ss_list

def get_block_snapshot_id(snapshot_name, host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f json block-snapshot list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get snapshot info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            snapshotinfo = json.loads(ret[0])
            snapshot_list = snapshotinfo["block_snapshots"]
            for s in snapshot_list:
                if s["name"] == snapshot_name:
                    return s["id"]
        except Exception as e:
            print "[Error] the error message is: " + e.message
    return retval

def update_block_snapshot(snapshot, name=None, description=None, host=None):
    raise NotImplementedError("This function is not implemented.")

if __name__ == "__main__":
    # create 1000 snapshots
    _, volume_ids = BlockVolume.get_block_volume_ids()
    for i in range(1, 1001):
        idx = random.randint(0, len(volume_ids))
        print create_block_snapshot("snapshot-" + str(uuid.uuid1()), volume_ids[idx])

    # run get_block_snapshot_ids x times
    length  = 100
    start = datetime.datetime.now()
    print start
    for i in range(length):
        get_block_snapshot_ids()
    end = datetime.datetime.now()
    print end
    print (end - start ).seconds / (length * 1.0)


    #host = "10.0.11.233"
    # update_block_snapshot("xxx")
    #print create_block_snapshot("snapshot1", "volume1")
    #print create_block_snapshot("snapshot1", "volume1", host=host)
    #print delete_block_snapshot("snapshot1")
    #print delete_block_snapshot("snapshot1", host=host)
