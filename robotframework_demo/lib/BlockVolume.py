#! /usr/bin/env python

import random
import json
import utils
import Pool

def create_block_volume(volume_name, pool, size, description='', format=128, performance_priority=0, qos_enabled=False, max_total_iops=0, max_total_bw=0, burst_total_iops=0, burst_total_iobw=0, host=None):
    """
    volume_name: volume name
    pool: pool id or name
    size: volume size, like 100M, 100G, or 100000. If the unit is ignored, the unit is byte.

    """
    retval = 0
    if not isinstance(pool, int):
        pool = Pool.get_pool_id(pool, host)
    if pool == -1:
        print "[Error] The pool id is invalid."
        return -1
    cmd = utils.XMS_CLI_HEADER + "-f json block-volume create -p {poolid} -s {volsize} -f {fmt} --pp {pp} {volname}".format(poolid=pool, volsize=size, fmt=format, pp=performance_priority, volname=volume_name)
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to create block volume " + str(volume_name) + ". Error message: [{err}]".format(err=ret[1])
        retval = -1
    return retval

def delete_block_volume(volume, host=None):
    retval = -1
    if type(volume) in (str, int):
        if isinstance(volume, str):
            volume = get_block_volume_id(volume, host)
            print "-----" + str(volume)
        if volume == -1:
            print "[Error] The volume %s is not existed" % volume
        else:
            cmd = utils.XMS_CLI_HEADER + "block-volume delete {id}".format(id=volume)
            ret = utils.execute_cmd_in_host(cmd, host)
            if ret[2] != 0:
                print "[Error] Failed to delete block volume " + str(volume) + ". Error message: [{err}]".format(err=ret[1])
            else:
                retval = 0
    return retval

def update_block_volume(volume_id, volume_name=None, description=None, size=None, flattened=None, performance_priority=None, qos_enabled=None, max_total_iops=None, max_total_bw=None, burst_total_iops=None, burst_total_iobw=None):
    raise NotImplementedError("This function is not implemented.")

def get_block_volume_ids(host=None):
    retval = -1
    volume_list = []

    cmd = utils.XMS_CLI_HEADER + "-f json block-volume list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get block volume info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            volumes_info = json.loads(ret[0])
            volumes = volumes_info['block_volumes']
            for v in volumes:
                volume_list.append(v['id'])
            retval = 0
        except Exception as e:
            print "[Error] The block volume info is invalid. Error message: " + e.message
    return retval, volume_list

def get_block_volume_id(volume_name, host=None):
    """
    return the block volume id according to the volume name.
    """
    cmd = utils.XMS_CLI_HEADER + "-f json block-volume list --name {name}".format(name=volume_name)
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or isinstance(ret[0], dict):
        print "[Error] Failed to get block volume info. Error message: [{err}]".format(err=ret[1])
        return -1
    try:
        volume_info = json.loads(ret[0])
        return volume_info["block_volumes"][0]["id"]
    except Exception as e:
        print "[Error] error message is: " + e.message
    return -1

# # TODO remove it
# def create_client_group(name, cgtype, codes, description=None, host=None):
#     """
#     :Param name:   
#         client group name
#     :Param cgtype: 
#         iSCSI or FC
#     :Param codes:  
#         for iSCSI, the codes are IP or IQN; for FC, they are WWN.
#     """
#     retval = -1
#     try:
#         if isinstance(codes, list):
#             codes = ",".join(codes)
#     except Exception as e:
#         print "[Error] The client group codes is not valid."
#     else:
#         print "---%s----" % cgtype
#         if cgtype not in ("iSCSI", "FC"):
#             print "[Error] The client group type is not valid."
#         else:
#             if description:
#                 cmd = utils.XMS_CLI_HEADER + "client-group create --type {cgtype} --codes {codes} --description {des} {name}".format(name=name, codes=codes, des=description, cgtype=cgtype)
#             else:
#                 cmd = utils.XMS_CLI_HEADER + "client-group create --type {cgtype} --codes {codes} {name}".format(name=name, codes=codes, cgtype=cgtype)
#             print cmd
#             ret = utils.execute_cmd_in_host(cmd, host)
#             if ret[2] != 0:
#                 print "[Error] Failed to create client group. Error message: [{err}]".format(err=ret[1])
#             else:
#                 retval = 0
#     return retval

# # TODO should be removed
# def create_access_path(name, aptype, description=None, chap=False, tname=None, tsecret=None, host=None):
#     retval = -1
#     if aptype not in ("iSCSI", "Local", "FC"):
#         print "[Error] The access path type is not valid."
#     else:
#         cmd = utils.XMS_CLI_HEADER + "access-path create --type {aptype} ".format(aptype=aptype)
#         if description:
#             cmd += "--description {des} ".format(des=description)
#         if chap and tname and tsecret:
#             cmd += "--chap {chap} --tname {tname} --tsecret {tsecret} ".format(chap=str(chap), tname=tname, tsecret=tsecret)
#         cmd += str(name)
#         print cmd
#         ret = utils.execute_cmd_in_host(cmd, host)
#         if ret[2] != 0:
#             print "[Error] Failed to create access path. Error message: [{err}]".format(err=ret[1])
#         else:
#             retval = 0
#     return retval

# # TODO should be removed
# def create_target(access_path, node, host=None):
#     retval = -1
#     if not isinstance(access_path, int):
#         access_path = get_access_path_id(access_path, host)
#     if not isinstance(node, int):
#         node = Host.get_host_id(node, host)
#     if access_path == -1 or node == -1:
#         print "[Error] The access path or host name/id is invalid."
#     else:
#         cmd = utils.XMS_CLI_HEADER + "target create --access-path {apid} --host {host_id}".format(apid=access_path, host_id=node)
#         ret = utils.execute_cmd_in_host(cmd, host)
#         if ret[2] != 0:
#             print "[Error] Failed to create target. Error message: [{err}]".format(err=ret[1])
#         else:
#             retval = 0
#     return retval

class BlockVolume(object):
    def __init__(self, vol_id, vol_name, client_group_num, pool_id, pool_name, access_path_id, access_path_name):
        self._id = vol_id
        self._name = vol_name
        self._client_group_num = client_group_num
        self._pool_id = pool_id
        self._pool_name = pool_name
        self._access_path_id = access_path_id
        self._access_path_name = access_path_name

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_client_group_num(self):
        return self._client_group_num

    def get_pool_id(self):
        return self._pool_id

    def get_pool_name(self):
        return self._pool_name

    def get_access_path_id(self):
        return self._access_path_id

    def get_access_path_name(self):
        return self._access_path_name

    def __str__(self):
        return "BlockVolume[id = {vid}, name = {vname}, client group nums = {cgn}, pool id = {pid}, pool name = {pn}, access path id = {apid}, access path name = {apname}]".format(vid=self._id, vname=self._name, cgn=self._client_group_num, pid=self._pool_id, pn=self._pool_name, apid=self._access_path_id, apname=self._access_path_name)

if __name__ == "__main__":
    pool_ids = Pool.get_pool_ids()
    for i in range(1, 2001):
        size = random.randint(100, 500)
        pool_id = pool_ids[random.randint(0, len(pool_ids))]
	#print i, size, pool_id
        print create_block_volume("volume-" + str(i), pool_id, str(size) + "G")
#    print get_block_volume_id("volumexxx")
#    print get_block_volume_id("volume1")
    # host = "10.0.11.233"
#    print get_block_volume_id("volumexxx", host)
#    print get_block_volume_id("volume1", host)
#    print "-----------1------------\n"
#    print delete_block_volume("xxx")
#    print delete_block_volume("xxx", host)
#    print delete_block_volume("volume1", host)
    # print "-----------2------------\n"
    #print create_block_volume("volume1", "pool1", "100G")
    #print create_block_volume("volume1", "pool1", "100G", host=host)
    #print create_block_volume("volume1", 5, "100G")
    #print create_block_volume("volume1", 5, "100G", host=host)
    #print Pool.get_pool_id("pool2")
    #print Pool.get_pool_id("pool2", host)
#
    #print create_block_volume("volume4", "pool1", "104G", host=host)
    #print create_block_volume("volume5", "pool2", "105G", host=host)
    #print delete_block_volume("volume4", host)
    #print delete_block_volume("volume5", host)
    #print get_block_volume_ids(host)

