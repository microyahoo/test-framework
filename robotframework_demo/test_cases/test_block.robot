*** Settings ***
Documentation          This example demonstrates executing a command on a remote machine
...                    and getting its output.
...
...                    Notice how connections are handled as part of the suite setup and
...                    teardown. This saves some time when executing several test cases.

Library                lib/Block.py

Suite Setup            Run Keywords     Remove Access Path Volumes         host=${host}     AND
...                                     Remove Mapping Groups              host=${host}     AND 
...                                     Remove Access Path Targets         host=${host}     AND
...                                     Remove Access Path                 host=${host}     AND
...                                     Remove Client Groups               host=${host}     AND
...                                     Remove Snapshots                   host=${host}     AND
...                                     Remove Block Volumes               host=${host}     AND
...                                     Wait For Teardown Completion       host=${host}

# Suite Teardown         Close All Connections

*** Variables ***
${host}                 10.0.11.233
${host1}                10.0.11.233
${host2}                10.0.11.234
${host3}                10.0.11.235
${host1_name}           node-233
${host2_name}           node-234
${host3_name}           node-235

@{client_groups}        client_group1    client_group2

${iscsi_type}           iSCSI
${local_type}           Local
# ${fc_type}              FC

@{iscsi_access_paths}   access-path1    access-path2    access-path3     access-path4    access-path5
@{local_access_paths}   access-path6    access-path7
${access_path1}         access-path1 
${access_path2}         access-path2 
${access_path3}         access-path3 
${access_path4}         access-path4 
${access_path5}         access-path5 
${access_path6}         access-path6
${access_path7}         access-path7 

@{pool_list}            pool1    pool2

${base}                 99
${from}                 100
${mid}                  105
${to_iscsi}             110
${to}                   115

**** Keywords ****
Only For Test
    Log     hello world

Check Whether Volumes Have Been Deleted
    [Arguments]    ${host}
    ${retval}=                      Get Block Volume Ids             host=${host}
    ${ret}=                         Evaluate                         ${retval}[0]
    @{volume_ids}=                  Evaluate                         ${retval}[1]
    ${len}=                         Get Length                       ${volume_ids}
    Log     ${ret}
    Log     ${len}
    Should Be Equal As Integers     ${ret}                            0
    Should Be Equal As Integers     ${len}                            0
    
Wait For Teardown Completion
    [Arguments]    ${host}
    Wait Until Keyword Succeeds	         15 min	        15 sec        Check Whether Volumes Have Been Deleted        host=${host}

*** Test Cases ***
Create Block Volumes
    [Documentation]     create multiple volumes in random size.
    @{volume_size_list}=     Evaluate       [x for x in range(${from}, ${to})]
    :FOR    ${item}    IN    @{volume_size_list}
    \    ${volume_name}=     Evaluate       "volume" + str($item - ${base})
    \    ${volume_size}=     Evaluate       str($item) + "G"
    \    ${pool_index}=      Evaluate       random.randint(0, len(@{pool_list}) - 1)     modules=random
    \    ${pool_name}=       Set Variable   @{pool_list}[${pool_index}]
    \    Run Keyword         Log            ${volume_name}
    \    Run Keyword         Log            ${volume_size}
    \    Run Keyword         Log            ${pool_index}
    \    Run Keyword         Log            ${pool_name}
    \    ${ret}=             Create Block Volume     ${volume_name}     ${pool_name}    ${volume_size}    host=${host}
    \    Should Be Equal As Integers     ${ret}     0

Create Snapshots
    [Documentation]     create multiple snapshots.
    @{volume_size_list}=       Evaluate       [x for x in range(${from}, ${to})]
    :FOR    ${item}    IN      @{volume_size_list}
    \    ${volume_name}=       Evaluate       "volume" + str(${item} - ${base})
    \    ${snapshot_name}=     Evaluate       "volume" + str(${item} - ${base}) + "_snapshot" + str(${item} - ${base})
    \    Run Keyword           Log            ${volume_name} 
    \    Run Keyword           Log            ${snapshot_name}
    \    ${ret}=               Create Block Snapshot       ${snapshot_name}       ${volume_name}       host=${host} 
    \    Should Be Equal As Integers     ${ret}     0

Create Iscsi Client Groups
    [Documentation]     create iSCSI client groups
    ${codes1}=                Catenate          SEPARATOR=,         ${host1}    ${host2} 
    ${codes2}=                Catenate          ${host3}
    ${ret}=                   Get Block Volume Ids     host=${host}
    Log                       ${ret}
    ${ret}=                   Create Client Group      @{client_groups}[0]       ${iscsi_type}       ${codes1}      host=${host} 
    Should Be Equal As Integers     ${ret}     0
    ${ret}=                   Create Client Group      name=@{client_groups}[1]       cgtype=${iscsi_type}      codes=${codes2}      host=${host} 
    Should Be Equal As Integers     ${ret}     0

Create Access Paths
    [Documentation]     create access paths
    @{iscsi_ap_length}=     Evaluate       [x for x in range(0, len(@{iscsi_access_paths}))]
    @{local_ap_length}=     Evaluate       [x for x in range(0, len(@{local_access_paths}))]
    :FOR    ${item}    IN    @{iscsi_ap_length}
    \       ${ret}=             Create Access Path           @{iscsi_access_paths}[${item}]         ${iscsi_type}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0
    :FOR    ${item}    IN    @{local_ap_length}
    \       ${ret}=             Create Access Path           @{local_access_paths}[${item}]         ${local_type}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0

Create Access Path Targets 
    [Documentation]     create access path targets
    @{iscsi_ap_length}=     Evaluate       [x for x in range(0, len(@{iscsi_access_paths}))]
    @{local_ap_length}=     Evaluate       [x for x in range(0, len(@{local_access_paths}))]
    :FOR    ${item}    IN    @{iscsi_ap_length}
    \       ${ret}=             Create Target         @{iscsi_access_paths}[${item}]         ${host1_name}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0
    \       ${ret}=             Create Target         @{iscsi_access_paths}[${item}]         ${host2_name}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0
    :FOR    ${item}    IN    @{local_ap_length}
    \       ${ret}=             Create Target         @{local_access_paths}[${item}]         ${host1_name}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0
    \       ${ret}=             Create Target         @{local_access_paths}[${item}]         ${host2_name}      host=${host}
    \       Should Be Equal As Integers     ${ret}     0
    ${ret}=             Create Target         ${access_path2}         ${host3_name}      host=${host}
    Should Be Equal As Integers     ${ret}     0

Create Access Path Iscsi Mapping Groups
    [Documentation]     create access path block volumes
    @{client_group_length}=     Evaluate       [x for x in range(0, len(@{client_groups}))]
    :FOR    ${item}    IN    @{client_group_length}
    \    @{volume_list}=     Evaluate       ["volume" + str(x - ${base}) for x in range(${from}, ${mid})]
    \    ${ret}=             Create Mapping Group     access_path=${access_path1}        block_volumes=@{volume_list}     client_group=@{client_groups}[${item}]       host=${host}
    \    Should Be Equal As Integers     ${ret}     0
    \    @{volume_list}=     Evaluate       ["volume" + str(x - ${base}) for x in range(${mid}, ${to_iscsi})]
    \    ${ret}=             Create Mapping Group     access_path=${access_path2}        block_volumes=@{volume_list}     client_group=@{client_groups}[${item}]       host=${host}
    \    Should Be Equal As Integers     ${ret}     0

Create Access Path Local Mapping Groups
    [Documentation]     create access path block volumes
    @{local_ap_length}=          Evaluate       [x for x in range(0, len(@{local_access_paths}))]
    @{volume_list}=              Evaluate       ["volume" + str(x - ${base}) for x in range(${to_iscsi}, ${to})]
    ${slice_num}=                Evaluate       len(@{volume_list})/len(@{local_ap_length})
    # @{volume_slice_list}=        Evaluate       [@{volume_list}[i: ${slice_num} + i] for i in range(0, len(@{volume_list}), ${slice_num})]
    @{volume_slice_list}=        Slice List In Equality          num=${slice_num}      total=@{volume_list} 
    :FOR    ${item}    IN    @{local_ap_length}
    \    @{volume_list}=     Evaluate       ["volume" + str(x - ${base}) for x in range(${to_iscsi}, ${to})]
    \    ${ret}=             Create Mapping Group     access_path=@{local_access_paths}[${item}]        block_volumes=@{volume_slice_list}[${item}]     client_group=@{client_groups}[${item}]       host=${host}
    \    Should Be Equal As Integers     ${ret}     0
