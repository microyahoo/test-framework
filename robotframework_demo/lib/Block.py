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

def get_pool_id(pool_name, host=None):
    """
    return the block volume id according to the volume name.
    """
    cmd = utils.XMS_CLI_HEADER + "-f json pool list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or isinstance(ret[0], dict):
        print "[Error] Failed to get pool info. Error message: [{err}]".format(err=ret[1])
        return -1
    try:
        pool_info = json.loads(ret[0])
        pools = pool_info["pools"]
        for p in pools:
            if pool_name == p["name"]:
                return p["id"]
    except Exception as e:
        print "[Error] error message is: " + e.message
    return -1

def create_block_volume(volume_name, pool, size, description='', format=128, performance_priority=0, qos_enabled=False, max_total_iops=0, max_total_bw=0, burst_total_iops=0, burst_total_iobw=0, host=None):
    """
    volume_name: volume name
    pool: pool id or name
    size: volume size, like 100M, 100G, or 100000. If the unit is ignored, the unit is byte.

    """
    retval = 0
    if not isinstance(pool, int):
        pool = get_pool_id(pool, host)
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


def create_block_snapshot(snapshot_name, block_volume, description=None, host=None):
    retval = 0
    if not isinstance(block_volume, int):
        block_volume = get_block_volume_id(block_volume, host)
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
        print "[Error] Failed to create block snapshot. Error message: [{err}]".format(err=ret[1])
        retval = -1
    return retval

def get_block_snapshot_ids(host=None):
    retval = -1
    ss_list = []
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


def create_access_path(name, aptype, description=None, chap=False, tname=None, tsecret=None, host=None):
    retval = -1
    if aptype not in ("iSCSI", "Local", "FC"):
        print "[Error] The access path type is not valid."
    else:
        cmd = utils.XMS_CLI_HEADER + "access-path create --type {aptype} ".format(aptype=aptype)
        if description:
            cmd += "--description {des} ".format(des=description)
        if chap and tname and tsecret:
            cmd += "--chap {chap} --tname {tname} --tsecret {tsecret} ".format(chap=str(chap), tname=tname, tsecret=tsecret)
        cmd += str(name)
        print cmd
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print "[Error] Failed to create access path. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

def delete_access_path(access_path, host=None):
    retval = -1
    if not isinstance(access_path, int):
        access_path = get_access_path_id(access_path, host)
    if access_path == -1:
        print "[Error] The access path name/id is invalid."
    else:
        cmd = utils.XMS_CLI_HEADER + "access-path delete {apid}".format(apid=access_path)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print "[Error] Failed to delete access path. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

def get_access_path_id(name, host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f '{{range .}}{{println .id}}{{end}}' access-path list -q name.raw:" + str(name)
    # cmd = utils.XMS_CLI_HEADER + "-f json access-path list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or ret[0] is None or len(ret[0]) == 0:
        print "[Error] Failed to get access path info. Error message: [{err}]".format(err=ret[1])
    # else:
    #     try:
    #         access_path_info = json.loads(ret[0])
    #         paths = access_path_info['access_paths']
    #         for p in paths:
    #             if p['name'] == str(name):
    #                 return p['id']
    #     except Exception as e:
    #         print "[Error] The access path info is invalid."
    else:
        try:
            return int(ret[0])
        except Exception as e:
             print "[Error] The access path info is invalid. Error message: [{err}]".format(err=ret[1])
    return retval

def get_target_ids(host=None):
    retval = -1
    target_ids = []
    retval, targets = get_target_list(None, host)
    if retval == 0 and len(targets) > 0:
        for t in targets:
            target_ids.append(t.get_id())
    return retval, target_ids

def get_target_list(access_path=None, host=None):
    """
    access_path: access path id or name. int -> id, str -> name
                 if not specified, return all targets.
    """
    retval = -1
    target_list = []
    cmd = utils.XMS_CLI_HEADER + "-f json target list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or ret[0] is None or len(ret[0]) == 0:
        print "[Error] Failed to get target info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            target_info = json.loads(ret[0])
            targets = target_info['targets']
            for t in targets:
                if access_path is None \
                    or isinstance(access_path, str) and t['access_path']['name'] == access_path \
                    or isinstance(access_path, int) and t['access_path']['id'] == access_path:
                    target_list.append(Target(t['id'], t['host']['id'], t['iqn'], 
                        t['access_path']['id'], t['status'], t['port']))
            retval = 0
        except Exception as e:
            print "[Error] The target info is invalid."
    return retval, target_list

def get_block_volume_ids_via_access_path(access_path=None, host=None):
    """
    access_path: access path id or name. int -> id, str -> name
                 if not specified, return all block volume ids.
    """
    retval = -1
    bv_ids = []
    retval, volumes = get_block_volume_list(access_path, host)
    if retval == 0 and len(volumes) > 0:
        for p in volumes:
            bv_ids.append(p.get_id())
    return retval, bv_ids

def get_block_volume_list(access_path=None, host=None):
    """
    access_path: access path id or name. int -> id, str -> name
                 if not specified, return all block volumes.
    """
    retval = -1
    volume_list = []
    cmd = utils.XMS_CLI_HEADER + "-f json block-volume list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or ret[0] is None or len(ret[0]) == 0:
        print "[Error] Failed to get block volume info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            volume_info = json.loads(ret[0])
            volumes = volume_info['block_volumes']
            for v in volumes:
                if v['access_path'] and (access_path is None \
                    or isinstance(access_path, str) and v['access_path']['name'] == access_path \
                    or isinstance(access_path, int) and v['access_path']['id'] == access_path):
                    volume_list.append(BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], v['access_path']['id'], v['access_path']['name']))
            retval = 0
        except Exception as e:
            print "[Error] The volume info is invalid. Error message: " + e.message
    return retval, volume_list

def create_target(access_path, node, host=None):
    retval = -1
    if not isinstance(access_path, int):
        access_path = get_access_path_id(access_path, host)
    if not isinstance(node, int):
        node = get_host_id(node, host)
    if access_path == -1 or node == -1:
        print "[Error] The access path or host name/id is invalid."
    else:
        cmd = utils.XMS_CLI_HEADER + "target create --access-path {apid} --host {host_id}".format(apid=access_path, host_id=node)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print "[Error] Failed to create target. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

def delete_target(target_id, host=None):
    retval = -1
    if not isinstance(target_id, int):
        print "[Error] The target id is invalid."
    else:
        cmd = utils.XMS_CLI_HEADER + "target delete {target}".format(target=target_id)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print "[Error] Failed to delete target. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

def get_access_path_ids(host=None):
    retval = -1
    path_ids = []
    retval, paths = get_access_path_list(host)
    if retval == 0 and len(paths) > 0:
        for p in paths:
            path_ids.append(p.get_id())
    return retval, path_ids

def get_access_path_list(host=None):
    retval = -1
    paths = []
    cmd = utils.XMS_CLI_HEADER + "-f json access-path list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to list access paths. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            ap_info = json.loads(ret[0])
            aps = ap_info['access_paths']
            for t in aps:
                paths.append(AccessPath(t['id'], t['name'], t['type'], 
                    t['status'], t['block_volume_num'], 
                    t['client_group_num'], t['description']))
            retval = 0
        except Exception as e:
            print "[Error] The access path info is invalid."
    return retval, paths

class AccessPath(object):
    def __init__(self, ap_id, ap_name, ap_type, status, volume_nums, client_group_nums, description):
        self._id = ap_id
        self._name = ap_name
        self._type = ap_type
        self._status = status
        self._volume_nums = volume_nums
        self._client_group_nums = client_group_nums
        self._description = description

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_status(self):
        return self._status

    def get_description(self):
        return self._description

    def get_volume_nums(self):
        return self._volume_nums

    def get_client_group_nums(self):
        return self._client_group_nums

    def __str__(self):
        return "AccessPath[id = {apid}, name = {apname}, type = {aptype}, status = {status}, volume nums = {vns}, client group nums = {cgs}, description = {description}]".format(apid=self._id, apname=self._name, aptype=self._type, status=self._status, vns = self._volume_nums, cgs = self._client_group_nums, description=self._description)

class Target(object):
    def __init__(self, target_id, host_id, iqn, ap_id, status, port=3260):
        self._id = target_id 
        self._host_id = host_id
        self._iqn = iqn,
        self._ap_id = ap_id
        self._status = status
        self._port = port

    def get_id(self):
        return self._id

    def get_host_id(self):
        return self._host_id

    def get_iqn(self):
        return self._iqn

    def get_access_path_id(self):
        return self._ap_id

    def get_status(self):
        return self._status

    def get_port(self):
        return self._port

    def __str__(self):
        return "Target[id = %d, host_id = %d, iqn = %s, access_path_id = %d, status = %s, port = %d" % (self._id, self._host_id, self._iqn, self._ap_id, self._status, self._port)

def create_client_group(name, cgtype, codes, description=None, host=None):
    """
    :Param name:   
        client group name
    :Param cgtype: 
        iSCSI or FC
    :Param codes:  
        for iSCSI, the codes are IP or IQN; for FC, they are WWN.
    """
    retval = -1
    try:
        if isinstance(codes, list):
            codes = ",".join(codes)
    except Exception as e:
        print "[Error] The client group codes is not valid."
    else:
        if cgtype not in ("iSCSI", "FC"):
            print "[Error] The client group type is not valid."
        else:
            if description:
                cmd = utils.XMS_CLI_HEADER + "client-group create --type {cgtype} --codes {codes} --description {des} {name}".format(name=name, codes=codes, des=description, cgtype=cgtype)
            else:
                cmd = utils.XMS_CLI_HEADER + "client-group create --type {cgtype} --codes {codes} {name}".format(name=name, codes=codes, cgtype=cgtype)
            print cmd
            ret = utils.execute_cmd_in_host(cmd, host)
            if ret[2] != 0:
                print "[Error] Failed to create client group. Error message: [{err}]".format(err=ret[1])
            else:
                retval = 0
    return retval

def delete_client_group(client_group, host=None):
    retval = -1
    if not isinstance(client_group, int):
        client_group = get_client_group_id(client_group, host)
    if client_group == -1:
        print "[Error] The client group name/id is invalid."
    else:
        cmd = utils.XMS_CLI_HEADER + "client-group delete {cgid}".format(cgid=client_group)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print "[Error] Failed to delete client group. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

def get_block_volume_ids_via_client_group(client_group, host=None):
    """
    access_path: client group id or name. int -> id, str -> name
                 if not specified, return all block volume ids.
    """
    retval = -1
    bv_ids = []
    retval, volumes = get_block_volume_list(client_group, host)
    if retval == 0 and len(volumes) > 0:
        for p in volumes:
            bv_ids.append(p.get_id())
    return retval, bv_ids

def get_block_volume_list(client_group, host="localhost"):
    retval = -1
    volume_list = []
    if type(client_group) in (str, int):
        if isinstance(client_group, str):
            client_group = get_client_group_id(client_group, host)
        if client_group != -1:
            token = utils.get_access_token(host)
            if token != -1:
                url = utils.XMS_REST_BASE_URL.format(ip=host) + "block-volumes/?token={token}\&client_group_id={cgid}" 
                curl_header = utils.XMS_CURL_GET_HEADER
                cmd = curl_header + url.format(token=token, cgid=client_group)
                # print cmd
                ret = utils.execute_cmd_in_host(cmd, host)
                if ret[2] != 0:
                    print "[Error] Failed to get client group volumes info. Error message: [{err}]".format(err=ret[1])
                else:
                    try:
                        volume_info = json.loads(ret[0])
                        volumes = volume_info['block_volumes']
                        for v in volumes:
                            if v['access_path']:
                                volume_list.append(BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], v['access_path']['id'], v['access_path']['name'])) 
                            else:
                                volume_list.append(BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], None, None))
                        retval = 0
                    except Exception as e:
                        print "[Error] The volumes info is invalid. Error message: " + e.message

    return retval, volume_list

def get_client_group_ids(host=None):
    retval = -1
    cgid_list = []
    cmd = utils.XMS_CLI_HEADER + "-f json client-group list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get client group info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            client_group_info = json.loads(ret[0])
            groups = client_group_info['client_groups']
            for g in groups:
                cgid_list.append(g['id'])
            retval = 0
        except Exception as e:
            print "[Error] The client group info is invalid. Error message: " + e.message
    return retval, cgid_list

def get_client_group_id(name, host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f json client-group list"
    print cmd
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get client group info. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            client_group_info = json.loads(ret[0])
            groups = client_group_info['client_groups']
            for g in groups:
                if g['name'] == name:
                    return g['id']
        except Exception as e:
            print "[Error] The client group info is invalid."
    return retval

def update_client_group(client_group, name=None, codes=None, description=None, host=None):
    raise NotImplementedError("This function is not implemented.")

class ClientGroup(object):
    # FIXME
    def __init__(self, cg_id, cg_name, cg_type=None, status=None, access_path_nums=None, block_volume_nums=None, client_nums=None, description=None):
        self._id = cg_id
        self._name = cg_name
        self._type = cg_type
        self._status = status
        self._access_path_nums = access_path_nums
        self._block_volume_nums = block_volume_nums
        self._client_nums = client_nums
        self._description = description

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_status(self):
        return self._status

    def get_access_path_nums(self):
        return self._access_path_nums

    def get_block_volume_nums(self):
        return self._block_volume_nums

    def get_client_nums(self):
        return self._client_nums

    def get_description(self):
        return self._description

    def __str__(self):
        return "ClientGroup[id = {cgid}, name = {cgname}, type = {cgtype}, status = {status}, access path nums = {apn}, block volume nums = {bvn}, client nums = {cn}, description = {des}".format(cgid=self._id, cgname=self._name, cgtype=self._type, status=self._status, apn=self._access_path_nums, bvn=self._block_volume_nums, cn=self._client_nums, des=self._description)

def create_mapping_group(access_path, block_volumes, client_group, host=None):
    """
    This method is used to create mapping group.

    :Param access_path: **Mandatory**. Expecting value is access path name or id.
    :Param block_volumes: **Mandatory**. Block volumes ids attached to this mapping group, seperated by comma: 1,2,3.
    :Param client_group: **Mandatory**. Client group id or name attached to this mapping group.
    :Param host: **Optional**. If host is None, it will run in the local.

    :returns: status
              0 success, -1 failed.

    """
    retval = -1
    if not isinstance(access_path, int):
        access_path = get_access_path_id(access_path, host)
    if not isinstance(client_group, int):
        client_group = get_client_group_id(client_group, host)
    if access_path == -1 or client_group == -1:
        print "[Error] The access path or client group name/id is invalid."
    else:
        try:
            retval, block_volumes = _handle_block_volumes(block_volumes, host)
            if retval != 0:
                return retval
        except Exception as e:
            print "[Error] The block volumes are not valid."
        else:
            cmd = utils.XMS_CLI_HEADER + "mapping-group create --access-path {ap} --block-volumes {bvs} --client-group {cg}".format(ap=access_path, bvs=block_volumes, cg=client_group)
            print cmd
            ret = utils.execute_cmd_in_host(cmd, host)
            if ret[2] != 0:
                retval = -1
                print "[Error] Failed to create mapping group. Error message: [{err}]".format(err=ret[1])
            else:
                retval = 0
    return retval

def _handle_block_volumes(block_volumes, host=None):
    print block_volumes
    retval = -1
    if type(block_volumes) not in (str, int, list):
        print "[Error] The block volume name {name} is not valid.".format(name=b)
        return retval, block_volumes

    if isinstance(block_volumes, str):
        block_volumes = [block_volumes]
        print block_volumes
    if isinstance(block_volumes, list):
        tmp = []
        for b in block_volumes:
            # change the volume name to id.
            if isinstance(b, str):
                bvid = get_block_volume_id(b, host)
                if bvid == -1:
                    print "[Error] The block volume name {name} is not valid.".format(name=b)
                    return retval, block_volumes
                tmp.append(str(bvid))
            elif isinstance(b, int):
                tmp.append(str(b))
        block_volumes = ",".join(tmp)
    return 0, str(block_volumes)
        

def delete_mapping_group(mg_id, host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "mapping-group delete {mgid}".format(mgid=mg_id)
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to delete mapping group. Error message: [{err}]".format(err=ret[1])
    else:
        retval = 0
    return retval

def _get_mapping_groups(host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f json mapping-group list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0:
        print "[Error] Failed to get mapping groups information. Error message: [{err}]".format(err=ret[1])
    else:
        try:
            return 0, json.loads(ret[0])
        except Exception as e:
            print "[Error] The mapping group info is invalid. Error message: " + e.message
    return retval, None

def get_client_groups_via_access_path(access_path=None, host=None):
    """
    return a dict of client groups for specified access path name/id, if access_path is not specified, return all client groups like below:
    {
        "access-path": [
            ClientGroup(),
            ClientGroup()
        ]
    }
    or
    {
        access_path_id: [
            ClientGroup(),
            ClientGroup()
        ]
    }
    or all client groups:
    {
        "access-path1": [
            ClientGroup()
        ],
        "access-path2": [
            ClientGroup(),
            ClientGroup()
        ]
    }
    """
    cg_dict = {}
    retval, mapping_groups = _get_mapping_groups(host)
    if retval == 0 and mapping_groups and isinstance(mapping_groups, dict) \
            and mapping_groups.has_key("mapping_groups"):
        mglist = mapping_groups["mapping_groups"]
        try:
            for mg in mglist:
                if access_path is None or isinstance(access_path, str) and mg['access_path']['name'] == access_path: 
                    ap_name = mg["access_path"]["name"]
                # if access_path is None or ap_name == access_path:
                    if not cg_dict.has_key(ap_name):
                        cg_dict[ap_name] = []
                    if mg["client_group"] is not None:
                        cg_dict[ap_name].append(ClientGroup(mg["client_group"]['id'], mg["client_group"]['name']))
                elif isinstance(access_path, int) and mg['access_path']['id'] == access_path:
                    ap_id = mg["access_path"]["id"]
                    if not cg_dict.has_key(ap_id):
                        cg_dict[ap_id] = []
                    if mg["client_group"] is not None:
                        cg_dict[ap_id].append(ClientGroup(mg["client_group"]['id'], mg["client_group"]['name']))
        except TypeError as e:
            print "[Error] The mapping group data is invalid. Error Message: " + e.message
        except Exception as e:
            print "[Error] " + e.message 
    return retval, cg_dict

def get_mapping_group_ids_via_access_path(access_path, host=None):
    """
    return a list of mapping group ids for specified access path
    """
    mg_list = []
    retval, mapping_groups = _get_mapping_groups(host)
    if retval == 0 and mapping_groups and isinstance(mapping_groups, dict) \
            and mapping_groups.has_key("mapping_groups"):
        mglist = mapping_groups["mapping_groups"]
        try:
            for mg in mglist:
                if mg['access_path'] and (access_path is None \
                    or isinstance(access_path, str) and mg['access_path']['name'] == access_path \
                    or isinstance(access_path, int) and mg['access_path']['id'] == access_path):
                # if mg["access_path"]["name"] == access_path:
                    mg_list.append(mg["id"])
        except TypeError:
            print "[Error] The mapping group data doesn't contain specified 'key'."
        except Exception as e:
            print "[Error] " + e.message 
    return retval, mg_list

def get_block_volume_ids_via_mapping_group(mapping_group, host=None):
    """
    mapping_group: mapping group id or name. int -> id, str -> name
                 if not specified, return all block volume ids.
    """
    retval = -1
    bv_ids = []
    retval, volumes = get_block_volume_list(mapping_group, host)
    if retval == 0 and len(volumes) > 0:
        for p in volumes:
            bv_ids.append(p.get_id())
    return retval, bv_ids

def get_block_volume_list(mapping_group, host="localhost"):
    retval = -1
    volume_list = []
    if isinstance(mapping_group, int):
        if mapping_group != -1:
            token = utils.get_access_token(host)
            if token != -1:
                url = utils.XMS_REST_BASE_URL.format(ip=host) + "block-volumes/?token={token}\&mapping_group_id={mgid}" 
                curl_header = utils.XMS_CURL_GET_HEADER
                cmd = curl_header + url.format(token=token, mgid=mapping_group)
                # print cmd
                ret = utils.execute_cmd_in_host(cmd, host)
                if ret[2] != 0:
                    print "[Error] Failed to get mapping group volumes info. Error message: [{err}]".format(err=ret[1])
                else:
                    try:
                        volume_info = json.loads(ret[0])
                        volumes = volume_info['block_volumes']
                        for v in volumes:
                            if v['access_path']:
                                volume_list.append(BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], v['access_path']['id'], v['access_path']['name'])) 
                            else:
                                volume_list.append(BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], None, None))
                        retval = 0
                    except Exception as e:
                        print "[Error] The volumes info is invalid. Error message: " + e.message

    return retval, volume_list

def add_block_volume(mg_id, block_volumes, host=None):
    """
    This method is used to add block volume(s) to a mapping group.

    :Param mg_id: **Mandatory**. Mapping group id.
    :Param block_volumes: **Mandatory**. Block volumes ids attached to this mapping group, seperated by comma: 1,2,3.
    """
    retval = -1
    try:
        retval, block_volumes = _handle_block_volumes(block_volumes, host)
        if retval != 0:
            return retval
    except Exception as e:
        print "[Error] The block volumes are not valid. Error Message: " + e.message
    else:
        cmd = utils.XMS_CLI_HEADER + "mapping-group add block-volume {mgid} {bvs}".format(mgid=mg_id, bvs=block_volumes)
        print cmd
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            retval = -1
            print "[Error] Failed to add mapping group block volumes. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval


def remove_block_volume(mg_id, block_volumes, host=None):
    """
    This method is used to remove block volume from a mapping group.

    :Param mg_id: **Mandatory**. Mapping group id.
    :Param block_volumes: **Mandatory**. Block volumes ids attached to this mapping group, seperated by comma: 1,2,3.
    """
    retval = -1
    try:
        retval, block_volumes = _handle_block_volumes(block_volumes, host)
        if retval != 0:
            return retval
    except Exception as e:
        print "[Error] The block volumes are not valid."
    else:
        cmd = utils.XMS_CLI_HEADER + "mapping-group remove block-volume {mgid} {bvs}".format(mgid=mg_id, bvs=block_volumes)
        print cmd
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            retval = -1
            print "[Error] Failed to remove mapping group block volumes. Error message: [{err}]".format(err=ret[1])
        else:
            retval = 0
    return retval

class MappingGroup(object):
    def __init__(self):
        pass

def remove_access_path_volumes(host=None):
    ret, apids = get_access_path_ids(host)
    print "[Info] access path ids = %s" % str(apids)
    if ret == 0:
        for apid in apids:
            print "\n > [Info] access path id = %d" % apid
            ret, mgids = get_mapping_group_ids_via_access_path(apid, host)
            if ret == 0:
                print "     >> [Info] mapping group ids = %s" % str(mgids)
                for mgid in mgids:
                    print "          >>> [Info] mapping group id = %d" % mgid
                    ret, volumes_ids = get_block_volume_ids_via_mapping_group(mgid, host)
                    if ret == 0:
                        for vid in volumes_ids:
                            print "               >>>> [Info] mapping group volume id = %d" % vid
                        if len(volumes_ids):
                            ret = remove_block_volume(mgid, volumes_ids, host)
                            if ret != 0:
                                print "[Error] Failed to remove block volumes from mapping group."
                    else:
                        print "[Error] Failed to get mapping group volumes info."

            else:
                print "[Error] Failed to get mapping group info."
    else:
        print "[Error] Failed to get access path info."

def remove_access_path_client_groups(host=None):
    ret, apids = get_access_path_ids(host)
    print "[Info] access path ids = %s" % str(apids)
    if ret == 0:
        for apid in apids:
            print "\n > [Info] access path id = %d" % apid
            ret, cgdict = get_client_groups_via_access_path(apid, host)
            if ret == 0:
                print cgdict
                if len(cgdict):
                    for cg in cgdict[apid]:
                        print cg
            else:
                print "[Error] Failed to get client groups info."
    else:
        print "[Error] Failed to get access path info."

def remove_mapping_groups(host=None):
    ret, apids = get_access_path_ids(host)
    print "[Info] access path ids = %s" % str(apids)
    if ret == 0:
        for apid in apids:
            print "\n > [Info] access path id = %d" % apid
            ret, mgids = get_mapping_group_ids_via_access_path(apid, host)
            if ret == 0:
                print "     >> [Info] mapping group ids = %s" % str(mgids)
                for mgid in mgids:
                    print "          >>> [Info] mapping group id = %d" % mgid
                    ret = delete_mapping_group(mgid, host)
                    if ret == 0:
                        print "[Info] Succeed to remove mapping group %d from access path." % mgid
                    else:
                        print "[Error] Failed to delete mapping group %d from access path." % mgid
            else:
                print "[Error] Failed to get mapping group info."
    else:
        print "[Error] Failed to get access path info."

def remove_access_path_targets(host=None):
    ret, target_ids = get_target_ids(host)
    if ret == 0:
        for tid in target_ids:
            print "\n > [Info] target id = %d" % tid
            ret = delete_target(tid, host)
            if ret == 0:
                print "[Info] Succeed to remove target %d from access path." % tid
            else:
                print "[Error] Failed to delete target %d from access path." % tid
    else:
        print "[Erro] Failed to get target info."

def remove_access_path(host=None):
    ret, apids = get_access_path_ids(host)
    print "[Info] access path ids = %s" % str(apids)
    if ret == 0:
        for apid in apids:
            print "\n > [Info] access path id = %d" % apid
            ret = delete_access_path(apid, host)
            if ret == 0:
                print "[Info] Succeed to remove access path %d." % apid
            else:
                print "[Error] Failed to delete access path %d." % apid
    else:
        print "[Error] Failed to get access path info."

def remove_client_groups(host=None):
    ret, cgid_list = get_client_group_ids(host)
    if ret == 0:
        for cgid in cgid_list:
            ret = delete_client_group(cgid, host)
            if ret == 0:
                print "[Info] Succeed to remove client group %d." % cgid
            else:
                print "[Error] Failed to delete client group %d." % cgid
    else:
        print "[Error] Failed to get client group info."

def remove_snapshots(host=None):
    ret, snapshotid_list = get_block_snapshot_ids(host)
    if ret == 0:
        for ssid in snapshotid_list:
            ret = delete_block_snapshot(ssid, host)
            if ret == 0:
                print "[Info] Succeed to remove snapshot %d." % ssid
            else:
                print "[Error] Failed to delete snapshot %d." % ssid
    else:
        print "[Error] Failed to get snapshot info."

def remove_block_volumes(host=None):
    ret, volumeid_list = get_block_volume_ids(host)
    if ret == 0:
        for volid in volumeid_list:
            ret = delete_block_volume(volid, host)
            if ret == 0:
                print "[Info] Succeed to remove block volume %d." % volid
            else:
                print "[Error] Failed to delete block volume %d." % volid
    else:
        print "[Error] Failed to get block volume info."

def slice_list_in_equality(num, total):
    if not isinstance(num, int) or not isinstance(total, list):
        print "[Error] Invalid type."
        return
    else:
        chunk_num = len(total) / num
        return [total[i:i + chunk_num] for i in range(0, len(total), chunk_num)]

if __name__ == "__main__":
    # l = [1, 2,3, 4, 5, 6, 7, 8,12, 23, 45, 56, 67, 78]
    l = [1, 2, 3, 4, 5]
    print slice_list_in_equality(2, l)
#    print get_block_volume_id("volumexxx")
#    print get_block_volume_id("volume1")
    host = "10.0.11.233"
#    print get_block_volume_id("volumexxx", host)
#    print get_block_volume_id("volume1", host)
#    print "-----------1------------\n"
#    print delete_block_volume("xxx")
#    print delete_block_volume("xxx", host)
#    print delete_block_volume("volume1", host)
    print "-----------2------------\n"
    print get_block_volume_ids(host)
    # print create_block_volume("volume1", "pool1", "100G")
    # print create_block_volume("volume1", "pool1", "100G", host=host)
    # print create_block_volume("volume1", 5, "100G")
    # print create_block_volume("volume1", 5, "100G", host=host)
    # print get_pool_id("pool2")
    # print get_pool_id("pool2", host)

    # print create_block_volume("volume4", "pool1", "104G", host=host)
    # print create_block_volume("volume5", "pool2", "105G", host=host)
    # print delete_block_volume("volume4", host)
    # print delete_block_volume("volume5", host)
    # print get_block_volume_ids(host)
