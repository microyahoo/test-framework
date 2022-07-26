#! /usr/bin/env python

import json
import os
import random
import time
import utils
import AccessPath
import BlockVolume
import ClientGroup

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
        access_path = AccessPath.get_access_path_id(access_path, host)
    if not isinstance(client_group, int):
        client_group = ClientGroup.get_client_group_id(client_group, host)
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
    #print block_volumes
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
                bvid = BlockVolume.get_block_volume_id(b, host)
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
                        cg_dict[ap_name].append(ClientGroup.ClientGroup(mg["client_group"]['id'], mg["client_group"]['name']))
                elif isinstance(access_path, int) and mg['access_path']['id'] == access_path:
                    ap_id = mg["access_path"]["id"]
                    if not cg_dict.has_key(ap_id):
                        cg_dict[ap_id] = []
                    if mg["client_group"] is not None:
                        cg_dict[ap_id].append(ClientGroup.ClientGroup(mg["client_group"]['id'], mg["client_group"]['name']))
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
                                volume_list.append(BlockVolume.BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], v['access_path']['id'], v['access_path']['name'])) 
                            else:
                                volume_list.append(BlockVolume.BlockVolume(v['id'], v['name'], v['client_group_num'], v['pool']['id'], v['pool']['name'], None, None))
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

if __name__ == "__main__":
    _, volume_ids = BlockVolume.get_block_volume_ids()
    _, client_group_ids = ClientGroup.get_client_group_ids()
    volume_ids.sort()
    client_group_ids.sort()
    cgid_len = len(client_group_ids)
    vid_len = len(volume_ids)

    for i in range(0, cgid_len/2):
        cgid = client_group_ids[i]
        print create_mapping_group(1, volume_ids[:vid_len/2], cgid)

    for i in range(cgid_len/2, cgid_len):
        cgid = client_group_ids[i]
        print create_mapping_group(2, volume_ids[vid_len/2:], cgid)

    # hostname = "10.0.11.233"
    # ret = _get_mapping_groups(hostname)
    # print type(ret)
    # print ret
    # access_path_id = AccessPath.get_access_path_id("access-path3", hostname)
    # print access_path_id
    # access_path_id = AccessPath.get_access_path_id("access-path", hostname)
    # print access_path_id
    # mg_ids = get_mapping_group_ids_via_access_path("access-path3", hostname)
    # print mg_ids
    # print "----begin to test in localhost"
    # ret = _get_mapping_groups()
    # print type(ret)
    # print ret
    # access_path_id = AccessPath.get_access_path_id("access-path3")
    # print access_path_id
    # access_path_id = AccessPath.get_access_path_id("access-path")
    # print access_path_id
    # mg_ids = get_mapping_group_ids_via_access_path("access-path3")
    # print mg_ids
    print "-----------------------------------------"
        
    # print create_mapping_group("access-path1", ["volume1", "volume2", "volume3"], "client_group1", hostname)
    # print create_mapping_group("access-path3", ["volume4", "volume5", "volume6", "volume7"], "client_group2", hostname)
    # print create_mapping_group("access-path2", ["volume8", "volume11", hostname)
    # print create_mapping_group("access-path5", ["volume9", "volume10", hostname)

    #print get_mapping_group_ids_via_access_path("access-path1", hostname)
    #print get_mapping_group_ids_via_access_path("access-path3", hostname)
    #ret, mgids = get_mapping_group_ids_via_access_path("access-path2", hostname)
    #if ret == 0:
        #for mgid in mgids:
            #print add_block_volume(mgid, "volume11", hostname)
            #time.sleep(15)
            #print remove_block_volume(mgid, "volume11", hostname)
#
    #print get_client_groups_via_access_path(host=hostname)
    #print get_client_groups_via_access_path("access-path1", host=hostname)
    #print "---------------------------2---------------------"
    #i, volumes = get_block_volume_list(66, host=hostname)
    #print i
    #if i == 0:
        #for v in volumes:
            #print v
    #print get_block_volume_ids_via_mapping_group(70, host=hostname)
