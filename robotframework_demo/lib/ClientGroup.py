#! /usr/bin/env python

import datetime
import random
import string
import uuid
import json
import utils
import BlockVolume

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
                print cmd
                ret = utils.execute_cmd_in_host(cmd, host)
                if ret[2] != 0:
                    print "[Error] Failed to get client group volumes info. Error message: [{err}]".format(err=ret[1])
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

def generate_iqn(vendor="xsky", cluster_name="cluster", ap_id=None):
    fields = string.ascii_letters + string.digits
    sn = "".join(random.sample(fields, 8))
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if ap_id is None:
        ap_id = random.randint(1, 10)
    return "iqn.%4d-%02d.%s:%s.iscsi.%d.%s" % (year, month, vendor, cluster_name, ap_id, sn)

if __name__ == "__main__":
    print generate_iqn()
    for i in range(1, 1001):
        iqn = generate_iqn()
        print create_client_group("client-group-" + str(i), "iSCSI", iqn)

    #host = "10.0.11.233"
    #host1 = "10.0.21.233"
    #host2 = "10.0.21.234"
    #host3 = "10.0.21.235"

    # print create_client_group("client_group1", "iSC", host1, host=host)
    # print create_client_group("client_group3", "FC", host1, host=host)
    # print create_client_group("client_group2", "iSCSI", [1, 2], host=host)
    # print create_client_group("client_group1", "iSCSI", host1, host=host)
    # print create_client_group("client_group2", "iSCSI", host2, host=host)
    # print create_client_group("client_group3", "iSCSI", host3, host=host)

    #print get_client_group_id('client_group1')
    #print get_client_group_id('client_group2')
    #print get_client_group_id('client_group3')
    #print get_client_group_id('client_group1', host)
    #print get_client_group_id('client_group2', host)
    #print get_client_group_id('client_group3', host)

    # print delete_client_group('client_group1', host=host)
    # print delete_client_group('client_group2', host=host)
    # print delete_client_group('client_group3', host=host)
    # print create_client_group("client_group1", "iSCSI", [host1, host3], host=host)
    # print create_client_group("client_group2", "iSCSI", [host2], host=host)

    # print delete_client_group('client_group1', host=host)
    # print delete_client_group('client_group2', host=host)
    #print "-------------------1----------------------"
    #i, volumes = get_block_volume_list("client_group1", host=host)
    #if i == 0:
        #for v in volumes:
            #print v
    #print "-------------------2----------------------"
    #i, volumes = get_block_volume_list("client_group2", host=host)
    #if i == 0:
        #for v in volumes:
            #print v
    #print get_block_volume_ids_via_client_group("client_group1", host=host)
    #print get_block_volume_ids_via_client_group("client_group2", host=host)
    #print get_client_group_ids(host)
