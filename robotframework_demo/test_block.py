#! /usr/bin/env python

import random
import uuid

import AccessPath
import BlockVolume
import ClientGroup
import Pool
import MappingGroup
import Snapshot


def just_for_test_block(volume_num=1000, volume_name_prefix="volume-", volume_size_min=100, volume_size_max=500, snapshot_num=1000, snapshot_name_prefix="snapshot-", client_group_num=1000, client_group_name_prefix="client-group", access_path_num=2, access_path_name_prefix="access_path", host=None):
    if access_path_num < 2 or volume_num < 2 or snapshot_num < 2 or client_group_num < 2:
        print "[Error] The num of access path, volume, snapshot, client group should be larger than 2."
        return
    if volume_size_min < 0 or volume_size_max < 0 or volume_size_min > volume_size_max:
        print "[Error] Invalid parameters."
        return

    # create block volumes 
    ret, pool_ids = Pool.get_pool_ids(host=host)
    if ret != 0 or len(pool_ids) < 1:
        print "[Error] Failed to get pool info or pool not exists."
        return
    for i in range(1, volume_num + 1):
        size = random.randint(volume_size_min, volume_size_max)
        pool_id = pool_ids[random.randint(0, len(pool_ids) - 1)]
        print BlockVolume.create_block_volume(volume_name_prefix + str(i), pool_id, str(size) + "G", host=host)

    # create block snapshots
    ret, volume_ids = BlockVolume.get_block_volume_ids(host=host)
    if ret != 0 or len(volume_ids) < 1:
        print "[Error] Failed to get volume info or volumes not exist."
        return
    for i in range(1, snapshot_num + 1):
        idx = random.randint(0, len(volume_ids) - 1)
        print Snapshot.create_block_snapshot(snapshot_name_prefix + str(uuid.uuid1()), volume_ids[idx], host=host)

    for i in range(1, client_group_num + 1):
        iqn = generate_iqn()
        print ClientGroup.create_client_group(client_group_name_prefix + str(i), "iSCSI", iqn, host=host)

    # create access paths
    for i in range(1, access_path_num + 1):
        print AccessPath.create_access_path(access_path_name_prefix + str(i), aptype="iSCSI", host=host)

    # create mapping groups
    ret, client_group_ids = ClientGroup.get_client_group_ids(host=host)
    if ret != 0:
        print "[Error] Failed to get client group info."
        return

    volume_ids.sort()
    client_group_ids.sort()

    cgid_len = len(client_group_ids)
    vid_len = len(volume_ids)

    for i in range(0, cgid_len/2):
        cgid = client_group_ids[i]
        print MappingGroup.create_mapping_group(1, volume_ids[:vid_len/2], cgid, host=host)

    for i in range(cgid_len/2, cgid_len):
        cgid = client_group_ids[i]
        print MappingGroup.create_mapping_group(2, volume_ids[vid_len/2:], cgid, host=host)

if __name__ == "__main__":
    just_for_test_block(
            volume_num=2,
            snapshot_num=2,
            client_group_num=2)

