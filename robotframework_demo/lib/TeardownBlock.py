#! /usr/bin/env python

import AccessPath
import BlockVolume
import ClientGroup
import MappingGroup
import Snapshot

def remove_access_path_volumes(host=None):
    ret, apids = AccessPath.get_access_path_ids(host)
    print("[Info] access path ids = %s" % str(apids))
    if ret == 0:
        for apid in apids:
            print("\n > [Info] access path id = %d" % apid)
            ret, mgids = MappingGroup.get_mapping_group_ids_via_access_path(apid, host)
            if ret == 0:
                print("     >> [Info] mapping group ids = %s" % str(mgids))
                for mgid in mgids:
                    print("          >>> [Info] mapping group id = %d" % mgid)
                    ret, volumes_ids = MappingGroup.get_block_volume_ids_via_mapping_group(mgid, host)
                    if ret == 0:
                        for vid in volumes_ids:
                            print("               >>>> [Info] mapping group\
                                  volume id = %d" % vid)
                        if len(volumes_ids):
                            ret = MappingGroup.remove_block_volume(mgid, volumes_ids, host)
                            if ret != 0:
                                print("[Error] Failed to remove block volumes\
                                      from mapping group.")
                    else:
                        print("[Error] Failed to get mapping group volumes\
                              info.")

            else:
                print("[Error] Failed to get mapping group info.")
    else:
        print("[Error] Failed to get access path info.")

def remove_access_path_client_groups(host=None):
    ret, apids = AccessPath.get_access_path_ids(host)
    print("[Info] access path ids = %s" % str(apids))
    if ret == 0:
        for apid in apids:
            print("\n > [Info] access path id = %d" % apid)
            ret, cgdict = MappingGroup.get_client_groups_via_access_path(apid, host)
            if ret == 0:
                print(cgdict)
                if len(cgdict):
                    for cg in cgdict[apid]:
                        print(cg)
            else:
                print("[Error] Failed to get client groups info.")
    else:
        print("[Error] Failed to get access path info.")

def remove_mapping_groups(host=None):
    ret, apids = AccessPath.get_access_path_ids(host)
    print("[Info] access path ids = %s" % str(apids))
    if ret == 0:
        for apid in apids:
            print("\n > [Info] access path id = %d" % apid)
            ret, mgids = MappingGroup.get_mapping_group_ids_via_access_path(apid, host)
            if ret == 0:
                print("     >> [Info] mapping group ids = %s" % str(mgids))
                for mgid in mgids:
                    print("          >>> [Info] mapping group id = %d" % mgid)
                    ret = MappingGroup.delete_mapping_group(mgid, host)
                    if ret == 0:
                        print("[Info] Succeed to remove mapping group %d from\
                              access path." % mgid)
                    else:
                        print("[Error] Failed to delete mapping group %d from\
                              access path." % mgid)
            else:
                print("[Error] Failed to get mapping group info.")
    else:
        print("[Error] Failed to get access path info.")

def remove_access_path_targets(host=None):
    ret, target_ids = AccessPath.get_target_ids(host)
    if ret == 0:
        for tid in target_ids:
            print("\n > [Info] target id = %d" % tid)
            ret = AccessPath.delete_target(tid, host)
            if ret == 0:
                print("[Info] Succeed to remove target %d from access path." %\
                      tid)
            else:
                print("[Error] Failed to delete target %d from access path." %\
                      tid)
    else:
        print("[Erro] Failed to get target info.")

def remove_access_path(host=None):
    ret, apids = AccessPath.get_access_path_ids(host)
    print("[Info] access path ids = %s" % str(apids))
    if ret == 0:
        for apid in apids:
            print("\n > [Info] access path id = %d" % apid)
            ret = AccessPath.delete_access_path(apid, host)
            if ret == 0:
                print("[Info] Succeed to remove access path %d." % apid)
            else:
                print("[Error] Failed to delete access path %d." % apid)
    else:
        print("[Error] Failed to get access path info.")

def remove_client_groups(host=None):
    ret, cgid_list = ClientGroup.get_client_group_ids(host)
    if ret == 0:
        for cgid in cgid_list:
            ret = ClientGroup.delete_client_group(cgid, host)
            if ret == 0:
                print("[Info] Succeed to remove client group %d." % cgid)
            else:
                print("[Error] Failed to delete client group %d." % cgid)
    else:
        print("[Error] Failed to get client group info.")

def remove_snapshots(host=None):
    ret, snapshotid_list = Snapshot.get_block_snapshot_ids(host)
    if ret == 0:
        for ssid in snapshotid_list:
            ret = Snapshot.delete_block_snapshot(ssid, host)
            if ret == 0:
                print("[Info] Succeed to remove snapshot %d." % ssid)
            else:
                print("[Error] Failed to delete snapshot %d." % ssid)
    else:
        print("[Error] Failed to get snapshot info.")

def remove_block_volumes(host=None):
    ret, volumeid_list = BlockVolume.get_block_volume_ids(host)
    if ret == 0:
        for volid in volumeid_list:
            ret = BlockVolume.delete_block_volume(volid, host)
            if ret == 0:
                print("[Info] Succeed to remove block volume %d." % volid)
            else:
                print("[Error] Failed to delete block volume %d." % volid)
    else:
        print("[Error] Failed to get block volume info.")

if __name__ == "__main__":
    host = "10.255.101.73"
    remove_access_path_volumes(host)
    # remove_access_path_client_groups(host)
    remove_mapping_groups(host)
    remove_access_path_targets(host)
    remove_access_path(host)
    remove_client_groups(host)
    remove_snapshots(host)
    remove_block_volumes(host)


