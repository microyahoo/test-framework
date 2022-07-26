#! /usr/bin/env python

import json
import utils
import Host
import BlockVolume

def create_access_path(name, aptype, description=None, chap=False, tname=None, tsecret=None, host=None):
    retval = -1
    if aptype not in ("iSCSI", "Local", "FC"):
        print("[Error] The access path type is not valid.")
    else:
        cmd = utils.XMS_CLI_HEADER + "access-path create --type {aptype} ".format(aptype=aptype)
        if description:
            cmd += "--description {des} ".format(des=description)
        if chap and tname and tsecret:
            cmd += "--chap {chap} --tname {tname} --tsecret {tsecret} ".format(chap=str(chap), tname=tname, tsecret=tsecret)
        cmd += str(name)
        print(cmd)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print("[Error] Failed to create access path. Error message:\
                  [{err}]".format(err=ret[1]))
        else:
            retval = 0
    return retval

def delete_access_path(access_path, host=None):
    retval = -1
    if not isinstance(access_path, int):
        access_path = get_access_path_id(access_path, host)
    if access_path == -1:
        print("[Error] The access path name/id is invalid.")
    else:
        cmd = utils.XMS_CLI_HEADER + "access-path delete {apid}".format(apid=access_path)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print("[Error] Failed to delete access path. Error message:\
                  [{err}]".format(err=ret[1]))
        else:
            retval = 0
    return retval

def get_access_path_id(name, host=None):
    retval = -1
    cmd = utils.XMS_CLI_HEADER + "-f '{{range .}}{{println .id}}{{end}}' access-path list -q name.raw:" + str(name)
    # cmd = utils.XMS_CLI_HEADER + "-f json access-path list"
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or ret[0] is None or len(ret[0]) == 0:
        print("[Error] Failed to get access path info. Error message:\
              [{err}]".format(err=ret[1]))
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
             print("[Error] The access path info is invalid. Error message:\
                   [{err}]".format(err=ret[1]))
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
        print("[Error] Failed to get target info. Error message:\
              [{err}]".format(err=ret[1]))
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
            print("[Error] The target info is invalid.")
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
    print(cmd)
    ret = utils.execute_cmd_in_host(cmd, host)
    if ret[2] != 0 or ret[0] is None or len(ret[0]) == 0:
        print("[Error] Failed to get block volume info. Error message:\
              [{err}]".format(err=ret[1]))
    else:
        try:
            volume_info = json.loads(ret[0])
            volumes = volume_info['block_volumes']
            for v in volumes:
                if v['access_path'] and (access_path is None \
                    or isinstance(access_path, str) and v['access_path']['name'] == access_path \
                    or isinstance(access_path, int) and v['access_path']['id'] == access_path):
                    volume_list.append(BlockVolume.BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], v['access_path']['id'], v['access_path']['name']))
            retval = 0
        except Exception as e:
            print("[Error] The volume info is invalid. Error message: " +\
                  e.message)
    return retval, volume_list

def create_target(access_path, node, host=None):
    retval = -1
    if not isinstance(access_path, int):
        access_path = get_access_path_id(access_path, host)
    if not isinstance(node, int):
        node = Host.get_host_id(node, host)
    if access_path == -1 or node == -1:
        print("[Error] The access path or host name/id is invalid.")
    else:
        cmd = utils.XMS_CLI_HEADER + "target create --access-path {apid} --host {host_id}".format(apid=access_path, host_id=node)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print("[Error] Failed to create target. Error message:\
                  [{err}]".format(err=ret[1]))
        else:
            retval = 0
    return retval

def delete_target(target_id, host=None):
    retval = -1
    if not isinstance(target_id, int):
        print("[Error] The target id is invalid.")
    else:
        cmd = utils.XMS_CLI_HEADER + "target delete {target}".format(target=target_id)
        ret = utils.execute_cmd_in_host(cmd, host)
        if ret[2] != 0:
            print("[Error] Failed to delete target. Error message:\
                  [{err}]".format(err=ret[1]))
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
        print("[Error] Failed to list access paths. Error message:\
              [{err}]".format(err=ret[1]))
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
            print("[Error] The access path info is invalid.")
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
 
if __name__ == "__main__":
    host = "10.0.11.233"
    host1 = "10.0.21.233"
    host2 = "10.0.21.234"
    host3 = "10.0.21.235"

    # t = Target(11, 23, 'xxxx', 33, 'active', 3260)
    # print t
    # print get_access_path_id("access-path1")
    # print get_access_path_id("access-path1", host)
    # print create_access_path("access-path2", "Local")
    # print create_access_path("access-path3", "xxLocal")
    # print create_access_path("access-path2", "iSCSI")
    # print create_access_path("access-path3", "iSCSI")
    # print create_access_path("access-path2", "Local", host=host)
    # print create_access_path("access-path3", "xxLocal", host=host)
    # print create_access_path("access-path1", "iSCSI", host=host)
    # print create_access_path("access-path2", "iSCSI", host=host)
    # print create_access_path("access-path3", "iSCSI", host=host)
    # print create_target("access-path1", "node-233", host)
    # print create_target("access-path1", "node-234", host)
    # print create_target("access-path1", "node-235", host)
    # print create_target("access-path2", "node-233", host)
    # print create_target("access-path2", "node-234", host)
    # print create_target("access-path2", "node-235", host)
    # print create_target("access-path3", "node-233", host)
    # print create_target("access-path3", "node-234", host)
    # print create_target("access-path3", "node-235", host)
    # print delete_access_path("access-path1")
    # print delete_access_path("access-path2")
    # print delete_access_path("access-path3")
    # print delete_access_path("access-path1", host)
    # print delete_access_path("access-path2", host)
    # print delete_access_path("access-path3", host)
    # print get_target_list("access-path1")
    # print "====================="
    # i, ap_list = get_target_list("access-path1", host)
    # if i == 0:
    #     for a in ap_list:
    #         print a
    # print get_target_list(11)
    # i, ap_list = get_target_list(11, host)
    # if i == 0:
    #     for a in ap_list:
    #         print a
    # i, ap_list = get_target_list(host=host)
    # if i == 0:
    #     for a in ap_list:
    #         print a
    # print "=========2==========="
    # i, ap_list = get_target_list(host=host)
    # if i == 0:
    #     for a in ap_list:
    #         print delete_target(a.get_id(), host)
    # print delete_access_path("access-path1") 
    # print delete_access_path("access-path2") 
    # print delete_access_path("access-path3") 
    # print delete_access_path("access-path1", host) 
    # print delete_access_path("access-path2", host) 
    # print delete_access_path("access-path3", host) 
    # print delete_access_path("access-path5", host) 
    print("=========3===========")
    i, aps = get_access_path_list(host)
    if i == 0:
        for a in aps:
            print(a)
    print(get_access_path_ids(host))
    print(get_target_ids(host))
    print("=========4===========")
    i, vols = get_block_volume_list(host=host)
    if i == 0:
        for v in vols:
            print(v)
    print("=========5===========")
    i, vols = get_block_volume_list("access-path3", host)
    if i == 0:
        for v in vols:
            print(v)
    print(get_block_volume_ids_via_access_path("access-path3", host))
    print(get_block_volume_ids_via_access_path(host=host))
    print(get_block_volume_ids_via_access_path())

