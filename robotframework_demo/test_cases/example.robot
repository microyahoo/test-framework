*** Settings ***
Documentation          This example demonstrates executing a command on a remote machine
...                    and getting its output.
...
...                    Notice how connections are handled as part of the suite setup and
...                    teardown. This saves some time when executing several test cases.

Library                SSHLibrary
Library                lib/IssueCmd.py 
Library                lib/MappingGroup.py 
Resource               resources/ssh.robot

Suite Teardown         Close All Connections

*** Variables ***
${host}                10.0.11.233
${accesspath}          access-path3 

*** Test Cases ***
Verify Access Path Output
    [Documentation]    Execute Command can be used to run commands on the remote machine.
    ...                The keyword returns the array of standard output, error output and return value.
    Log    %{ENV_XMS_CLI_USER}
    Log    %{ENV_BJ}
    Log    %{ENV_SZ}
    Log    %{ENV_XMS_CLI_PWD}
    ${output}=         Issue Cmd Via Root    xms-cli --user %{ENV_XMS_CLI_USER} --password %{ENV_XMS_CLI_PWD} access-path list   host=${host}
    Log    %{OUTPUT}
    Should Contain    ${output}[0]          access-path3
    Should Contain    %{OUTPUT}             access-path3

Verify Block Volume List Output
    [Documentation]     Test volume list output
    [Setup]             Open Connection And Log In    host=${host}
    ${output}=          Execute Command    xms-cli --user %{ENV_XMS_CLI_USER} --password %{ENV_XMS_CLI_PWD} block-volume list
    Should Contain      ${output}    testvolume

Verify Access Path Id
    [Documentation]     Test access path id
    ${id}=      Get Access Path Id   access_path=${accesspath}    host=${host}
    Should Be Equal As Integers     ${id}       6

Verify Block Volume Output
    [Documentation]    Execute Command can be used to run commands on the remote machine.
    ${output}=         Issue Cmd Via Root    xms-cli --user %{ENV_XMS_CLI_USER} --password %{ENV_XMS_CLI_PWD} block-volume list   host=${host}
    Log    %{OUTPUT}
    Should Contain    ${output}[0]          testvolume
    Should Contain    %{OUTPUT}             testvolume
    Should Match Regexp     %{OUTPUT}       testvolume\\s+\\|\\s+\\d+.*pool1

Verify Mapping Group Ids
    [Documentation]    Execute Command can be used to run commands on the remote machine.
    ${ids}      Get Mapping Group Id Via Access Path        access_path=${accesspath}    host=${host}
    Log     ${ids}

Verify Client Group Output
    [Documentation]    Execute Command can be used to run commands on the remote machine.
    ${output}=         Issue Cmd Via Root    xms-cli --user %{ENV_XMS_CLI_USER} --password %{ENV_XMS_CLI_PWD} client-group list   host=${host}
    Log    %{OUTPUT}
    Should Contain    ${output}[0]          iscsi233
    Should Contain    %{OUTPUT}             iscsi233

Verify Mapping Group Output
    [Documentation]    Execute Command can be used to run commands on the remote machine.
    ${output}=         Issue Cmd Via Root    xms-cli --user %{ENV_XMS_CLI_USER} --password %{ENV_XMS_CLI_PWD} mapping-group list   host=${host}
    Log    %{OUTPUT}
    Should Contain    ${output}[0]          iscsi233
    Should Contain    %{OUTPUT}             iscsi233
