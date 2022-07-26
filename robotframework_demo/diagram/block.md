## 1. 创建卷
```
Request URL: http://10.255.101.26:8056/api/v1/block-volumes
Request Method: POST
Request Payload:
    创建卷：
    block_volume: {
        format: 129,
        name: "volume1",
        performance_priority: 0,
        pool_id: 6,
        qos: {
            burst_total_bw: 2097152000,
            burst_total_iops: 200000,
            max_total_bw: 1048576000,
            max_total_iops: 100000,
        },  
        qos_enabled: true,
        size: 107374182400
    }
    克隆卷：
    block_volume: {                                                                                                               
        block_snapshot_id: 1,
        flattened: false,
        name: "snap_clone",
        performance_priority: 0,
        pool_id: 6,
        qos: {
            burst_total_bw: 209715200000,
            burst_total_iops: 200000,
            max_total_bw: 104857600000,
            max_total_iops: 100000,
        },
        qos_enabled: true
    }
```
- 首先判断token是否有效
- 然后将request payload转化为struct数据。
- 判断请求是否来自于source端。
- 根据pool ID判断pool的类型和状态。
- 判断数据库中是否存在此volume
- 如果设置了Qos，则判断qos结构体是否为空。
- 根据payload中是否包含snapshot ID来决定action类型是`create`或`clone`。
    - 如果是`create`类型
      - 判断volume size是否合适，最大512TB。
      - 根据request数据初始化models.Volume,并为其生成SN。
      - 如果request中format和Qos不为空，则设置volume format，在数据库中插入volume qos spec。
      - 在数据库中插入volume信息。
      - 创建`TaskTypeCreateBlockVolume` task，数据格式如下：
        ```
        { block_volume: { id: xxx }}
        ``` 
      - 如果from source，同时replicated volume不为空
        ```
        { block_volume: { id: xxx, replicated: true}}
        ```
      - task扫描到任务之后，修改数据库状态，然后调用rbd命令创建volume。
        ```
        rbd create <pool/image> --size <size> --image-format <format>
        ```
      - 如果需要设置PerformancePriority，则调用:
        ```
        rbd flags <pool/image> --set perf_vol
        ```
      - 如果是replicated volume，在数据库中插入一条progress info记录，创建一个`TaskTypeSetBlockVolumeReplication` task
        - [ ] **TODO**.......
      - 最后校验PerformancePriority，即只有V3卷才支持。
    - 如果是`clone`类型
      - 根据snapshot ID从数据库中读取指定的snapshot
      - 如果此snapshot属于某个volume group则不能被clone。
        - [ ] why?
      - 判断需要clone的snapshot是否关联volume。
        - 如果snapshot关联的volume是V2卷，同时pool类型为EC pool，则==不支持==。
        - pool类型有两种，replicated和EC。
      - 校验PerformancePriority。
      - 如果需要clone的volume的flattened为false，则检查clone chain level，最大16。如果为true，则检查pool大小。
        - [ ] stats?
      - 创建models.Volume，其中会为其关联`snapshot`。
      - 如果flattened为true，则会在数据库中创建progress info。
      - 创建`TaskTypeCloneBlockVolume` task，数据格式如下：
        ```
        { block_volume: { id: xxx }}
        ```   
      - 用到的命令行如下：
        ```
        rbd snap protect srcpool/srcimage@srcsnapshot
        rbd clone srcpool/srcimage@srcsnapshot dstpool/destimage
        rbd flatten pool/image
        ceph daemon /var/run/ceph/xbd-pc.asok perf dump libxbd-progress-<pool/volume>
        ```
        [ ] NewCommand("").WithRollback()
      - 最后更新数据库volume `Status, Snapshot, AllocatedSize`信息，如果flatten为true，会把`snapshot`置为`nil`。

---
## 2. 更新卷
```
Request URL: http://10.255.101.26:8056/api/v1/block-volumes
Request Method: PATCH
Request Payload:
    断开关系链：
    block_volume: {
        flattened: true
    }
    性能优先级设置：
    block_volume: {
        performance_priority: 1
    }
    设置QoS：
    block_volume: {
        qos: {
                burst_total_bw: 209715200000,
                burst_total_iops: 200000,
                max_total_bw: 104857600000,
                max_total_iops: 100000,
            },
            qos_enabled: true
        }
    }
    扩容/缩容卷：
    block_volume: {
        size: 161061273600
    }
    编辑：
    block_volume: {
        name: "vol3"
    }
    回滚：
    block_volume: {
        block_snapshot_id: 132, 
        action: "roll_back"
    }
```
- Note:
    - 如果卷关联了访问路径，则不允许缩容/回滚。
    - 如果卷为passive模式，则不允许调整大小，flatten和回滚。
    - 不允许在快照复制时对slave卷进行回滚。
    - 当卷属于某个volume group时不能回滚。
- 如果是调整卷大小，更新QoS，或者修改Performance Priority，则创建`TaskTypeUpdateBlockVolume` task。
    - 设置QoS
        - 如果卷关联了访问路径，且访问路径关联了targets，则在target所在的host上执行xdc命令更新，如下所示：
        ```
        xdcadm -L at -m lun -o update --lunname <volume> --name bps_total --value <bpsMax,bpsBurst>
        xdcadm -L at -m lun -o update --lunname <volume> --name ops_total --value <iopsMax,iopsBurst>
        ```
    - 调整大小
        ```
        rbd resize --allow-shrink --size <sizeMB> <pool/imageName>
        ```
        - 如果卷关联了访问路径，且访问路径关联了targets，则在target所在的host上执行xdc命令更新，如下所示：
        ```
        xdcadm -L at -m lun -o --lunname <vname> --lunsize <size>
        rbd du <pool/image>
        ```
    - 设置Performance Priority
        ```
        rbd flags <pool/image> --set perf_vol
        rbd flags <pool/image> --unset perf_vol
        ```
- 回滚
    - 创建`TaskTypeRollBackBlockVolume` task
    ```
    {
        block_volume: { id : volumeID},
        block_snapshot_id: blockSnapshotID,
        backup_block_snapshot_id: backupSnapshotID
    }
    ```
    - 创建backup snapshot
    ```
    rbd snap create <pool/volume@backupSnapshot>
    rbd du <pool/volume@backupSnapshot>
    ```
    - 异步回滚volume
    ```
    rbd snap rollback <pool/volume@snapshot>
    ceph daemon /var/run/ceph/xbd-pc.asok perf dump libxbd-progress-<pool/volume>
    rbd du <pool/volume>
    ```
- Flatten
    - 创建`TaskTypeFlattenBlockVolume` task
    ```
    {
        block_volume: { id : volumeID},
        flattened: <flattened>
    }
    
    ```
    - 异步执行flatten volume
    ```
    rbd flatten <pool/image>
    ceph daemon /var/run/ceph/xbd-pc.asok perf dump libxbd-progress-<pool/volume>
    rbd du <pool/volume>
    ```
---
## 3. 删除卷
```
Request URL: http://10.255.101.26:8056/api/v1/block-volumes/<volumeID>?force=<false>
Request Method: DELETE
```
- 首先根据指定的volume ID获取相应的volume `lock`。
- 如果能获取到lock，则从数据库读取相应的volume。
- 检查volume是否为passive模式。
- 检查volume所在的pool的状态。
- 有以下几种情况不能删除卷：
    - volume关联了snapshot
    - volume被添加到访问路径
    - volume属于某个volume group
- 创建`TaskTypeDeleteBlockVolume` task
```
{
    block_volume: { id : volumeID},
}
```
- 删除卷上的快照
  -  [ ] ??
```
rbd snap list <pool/image>
rbd snap unprotect <pool/image@snapshot>
rbd snap rm <pool/image@snapshot>
```
- 异步删除卷
```
rbd rm <pool/image>
ceph daemon /var/run/ceph/xbd-pc.asok perf dump libxbd-progress-<pool/volume>
```
- 如果不是Hidden卷，则将其从统计卷中删除
- 最后从数据库中删除

---
## 4. 创建快照
```
Request URL: http://10.255.101.26:8056/api/v1/block-snapshots
Request Method: POST
Request Payload:
    block_snapshot: {
        block_volume_id: 1,
        name: "volume1_snap"
    }
```
- 首先从数据库读取相应的volume。
- 根据指定的volume ID获取相应的volume `lock`。
- 如果能获取到lock，则检查pool和volume的状态。
- 检查volume的快照数量，最多只能创建256个快照。
- 查找数据库看是否存在要创建的快照，如果不存在则在数据库中添加相应的快照记录。
- 创建`TaskTypeCreateBlockSnapshot` task
```
    block_snapshot: {
        block_volume_id: <snapshot_id>
    }
```
```
rbd snap create <pool/image@snapshot>
对于非V2卷，会更新Allocated size
rbd du <pool/volume@snapshot>
```

---
## 5. 删除快照
```
Request URL: http://10.255.101.26:8056/api/v1/block-snapshots/<snapshot_id>?force=<false>
Request Method: DELETE
```

---
## 6. VIP
#### - 删除VIP group
```
Request URL: http://10.252.3.204:8056/api/v1/vip-groups/1
Request Method: DELETE
```
```
Request URL: http://10.252.3.204:8056/api/v1/network-addresses/?limit=-1&vip_group_id=1
Request Method: GET
Query String Parameters:
    limit: -1
    resource_id: 1
    resource_type: access_path
    
Request URL: http://10.252.3.204:8056/api/v1/vip-groups/?limit=-1&resource_id=2&resource_type=access_path
Request Method: GET
Query String Parameters:
    limit: -1
    resource_id: 2
    resource_type: access_path

Request URL: http://10.252.3.204:8056/api/v1/network-addresses/?host_id=1&limit=-1&role=gateway
Request Method: GET
Query String Parameters:
    host_id: 1
    limit: -1
    role: gateway
```

```
[root@chenhong204 ~]# ip addr
enp2s0f3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP qlen 1000
    link/ether 10:05:ca:9d:9b:9b brd ff:ff:ff:ff:ff:ff
    inet 10.252.1.204/24 brd 10.252.1.255 scope global enp2s0f3
       valid_lft forever preferred_lft forever
    inet 10.252.1.129/32 scope global enp2s0f3
       valid_lft forever preferred_lft forever
    inet 10.252.1.128/32 scope global enp2s0f3
       valid_lft forever preferred_lft forever
    inet6 fe80::455e:fbe2:1db5:64fe/64 scope link 
       valid_lft forever preferred_lft forever
```
#### - 创建VIP group
```
Request URL: http://10.252.3.204:8056/api/v1/vip-groups
Request Method: POST
Request Payload:
    vip_group: {
        network: "10.252.1.0/24",
        preempt: true,
        resource_id: 2,
        resource_type: "access_path",
        vips: [
            {
                ip: "10.252.1.128", 
                mask: 32, 
                network_address_id: 3
            },
            {
                ip: "10.252.1.129", 
                mask: 32, 
                network_address_id: 3
            }
        ]
    }
```
Note:   <++controllers/access_path_vip.go++>
- 一个访问路径最多关联 4 个 VIP 组。
- 最多支持 8 个访问路径启动 VIP 功能。
- 1个vip组最多16个vip
```
[root@chenhong204 ~]# tcpdump -n -c 10 -i enp2s0f3 vrrp
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on enp2s0f3, link-type EN10MB (Ethernet), capture size 262144 bytes
22:24:00.320720 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.321535 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.324482 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.324796 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.325251 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.325847 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.325895 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.326698 IP 10.252.1.68 > 224.0.0.18: VRRPv2, Advertisement, vrid 19, prio 101, authtype simple, intvl 1s, length 20
22:24:00.326731 IP 10.252.1.194 > 224.0.0.18: VRRPv2, Advertisement, vrid 7, prio 101, authtype simple, intvl 1s, length 20
22:24:00.327517 IP 10.252.1.194 > 224.0.0.18: VRRPv2, Advertisement, vrid 7, prio 101, authtype simple, intvl 1s, length 20
10 packets captured
11 packets received by filter
0 packets dropped by kernel
```

keepalived service: ++rpc/agent/keepalived.go++

1.  创建`TaskTypeCreateVIPGroup` task
```
{
    vip_group: { id: vgid }
}
```
- subtask `TaskTypeAccessPathCreateVIPGroup`
```
{
    "disable_notification": true,
    "access_path": {
        id: vg.ResourceID
    },
    "vip_group": {
        id: vg.ID
    }
}
```
- 将原有的gateway IP list对应的target portal移除，`RemovePortal()`
    - TODO
    
```
    xdcadm -L at --mode target --op remove --atid <atID> --iqn <iqn> --port <ip:port>
```
- 添加VIP portal，`AddPortal()`
```
    xdcadm -L at --mode target --op add --atid <atID> --iqn <iqn> --port <ip:port>
```

rpc/agent/keepalived.go   ->  `ScanVRIDs()`

    tcpdump -n -c <count> -i <interface> vrrp

rpc/agent/keepalived.go   -> `CreateKeepalivedInstance()`
```
    systemctl enable <.service>
    systemctl daemon-reload
    systemctl start <.service>
    /usr/sbin/keepalived -D --vrrp -f keepalived.conf -p keepalived.pid -r vrrp.pid
```

2. task `TaskTypeVIPGroupRemoveNetworkAddress`
3. task `TaskTypeVIPGroupAddNetworkAddress`

#### - 删除VIP
```
Request URL: http://10.252.3.204:8056/api/v1/vips/5
Request Method: DELETE
```
   - 根据VIP ID获取指定的VIP
   - 获取VIP resource lock
   - 检查VIP所在的VIP group的状态，并统计VIP group上的VIP的个数，不允许删除最后的一个VIP
   - 每一种resource type有其对应的checker，检查其checker是否存在（注册）
   - 检查resource的状态
   - 将VIP group的`ActionStatus`设置为`StatusUpdating`
   - 将VIP的`Status`设置为`StatusDeleting`
   - 获取VIP所对应的所有VIP instances，将其所有的instances的`Status`设置为`StatusDeleting`
   - 创建task `TaskTypeDeleteVIP`，对应的数据为：
   ```
       {
           vip: {
               id: <vip.ID>
           }
       }
   ```
   - task process()
     - `deleteKeepalivedForVIP(vg, vip, instances)`
        - 获取VIP group对应的所有NetworkAddresses
        - `DeleteKeepalivedForVIP(vg, vip, instances, rpcClientsMap)`
            - `DeleteOneKeepalivedInstance(vip, instance, client) `
                - `DeleteKeepalivedInstance()`
                ```
                   - systemctl stop <.service>
                   - systemctl disable <.service>
                   - remove directory
                   - systemctl daemon-reload
                ```
     - 创建subtask `removeVIP` `AccessPathRemoveVIP`   <<== <++tasks/access_path_vip.go++>
     ```
     {
         disable_notification: true,
         access_path: { id: <ap_id> },
         vip: { id: <vip_id> }
     }
     ```
        - - 获取access path
        - - 获取VIP
        - - 获取access path所有的targets
        - - `switchTargetToPhysicalPortal(target, []*models.VIP{vip}, true) `
            - RemovePortal()
            ```
            xdcadm -L at --mode target --op remove --atid <atID> --iqn <iqn> --port <ip:port>
            ```
        - - 更新access path `ActionStatus`为`Active`
     -  从数据库中删除对应的vip instances，VIP，修改VIP group的`ActionStatus`为`Active`

####  - 创建VIP
```
Request URL: http://10.252.3.204:8056/api/v1/vips
Request Method: POST
Request Payload:
    { 
        vip: {
            vip_group_id: 2, 
            ip: "10.252.1.129", 
            mask: 32, 
            network_address_id: 3
        }
    }
```
- 根据VIP group ID获取指定的VIP group
- 

#### ***Questions:*** 
- keepalived
- subnet, mask
- Signal USR1, HUP, USR2
- systemctl daemon-reload
- `AddVolumesToMappingGroup`  `orm.QueryM2M`
- docker NET_ADMIN

---
## 7. 数据保护
crypto_key.go

import offset length

---
## 8. CHAP
```
Request URL: http://10.255.101.73:8056/api/v1/access-paths/1
Request Method: PATCH
Request Payload:
{
    access_path: {
        name: "access_path1", 
        chap: true, 
        tname: "1qaz2wsx3edc", 
        tsecret: "1qaz2wsx3edc"
    }
}
```

```
Request URL: http://10.255.101.73:8056/api/v1/client-groups/1
Request Method: PATCH
Request Payload:
    {
        client_group: {
            chap: true, 
            iname: "3edc2wsx1qaz", 
            isecret: "3edc2wsx1qaz"
        }
    }

```

```
# *************
# CHAP Settings
# *************

# To enable CHAP authentication set node.session.auth.authmethod
# to CHAP. The default is None.
node.session.auth.authmethod = CHAP

# To set a CHAP username and password for initiator
# authentication by the target(s), uncomment the following lines:
node.session.auth.username = 1qaz2wsx3edc
node.session.auth.password = 1qaz2wsx3edc

# To set a CHAP username and password for target(s)
# authentication by the initiator, uncomment the following lines:
node.session.auth.username_in = 3edc2wsx1qaz
node.session.auth.password_in = 3edc2wsx1qaz
```

```
(ENV) [root@ceph-1 ~]# systemctl restart iscsid
(ENV) [root@ceph-1 ~]# iscsiadm -m discovery -t sendtargets -p 10.255.101.74:3260
10.255.101.74:3260,1 iqn.2019-01.com.xsky:testcluster.iscsi.1.14e203c25aeaaab5
(ENV) [root@ceph-1 ~]# iscsiadm -m node --targetname iqn.2019-01.com.xsky:testcluster.iscsi.1.14e203c25aeaaab5 10.255.101.74:3260 -l
Logging in to [iface: default, target: iqn.2019-01.com.xsky:testcluster.iscsi.1.14e203c25aeaaab5, portal: 10.255.101.74,3260] (multiple)
Login to [iface: default, target: iqn.2019-01.com.xsky:testcluster.iscsi.1.14e203c25aeaaab5, portal: 10.255.101.74,3260] successful.
```

```
[root@ceph-2 ~]# xdcadm -L at -m at -o show
Access Target information:
    AT 1:
        atid: 1
        boardid: 0
        hostname: ceph-2
        type: iscsi
        chap: user: 1qaz2wsx3edc password: 1qaz2wsx3edc
        targetlist:
            iqn: iqn.2019-01.com.xsky:testcluster.iscsi.1.14e203c25aeaaab5
            state: Enable
            portlist:
                portal IP: 10.255.101.74 port: 3260 flag: 0 mode: 0
        lunlist:
            lun id: 0 name: volume-e1ca0819025e46fcac9d8b61379baf81 sn: 1c5a53c025ad131a size: 214748364800 config: ceph/pool-04df31bcc71242709ca99199dffbf3fe/volume-e1ca0819025e46fcac9d8b61379baf81
            lun id: 1 name: volume-7d574a1969c0474cb784740d030e6da1 sn: 134587c046dae13e size: 214748364800 config: ceph/pool-04df31bcc71242709ca99199dffbf3fe/volume-7d574a1969c0474cb784740d030e6da1
        clientlist:
            client iqn: 10.255.101.73
            chap mutual: user: 3edc2wsx1qaz password: 3edc2wsx1qaz
            client lun mapping flag: mask
            client lun mapping list:
                client iqn: 10.255.101.73 lun sn: 1c5a53c025ad131a lunid: 0
            client iqn: 10.255.101.74
            chap mutual: user: 3edc2wsx1qaz password: 3edc2wsx1qaz
            client lun mapping flag: mask
            client lun mapping list:
                client iqn: 10.255.101.74 lun sn: 1c5a53c025ad131a lunid: 0
            client iqn: 10.200.39.15
            chap mutual: user:  password:
            client lun mapping flag: mask
            client lun mapping list:
                client iqn: 10.200.39.15 lun sn: 1c5a53c025ad131a lunid: 0
            client iqn: iqn.1994-05.com.redhat:9f2838fc926e
            chap mutual: user:  password:
            client lun mapping flag: mask
            client lun mapping list:
                client iqn: iqn.1994-05.com.redhat:9f2838fc926e lun sn: 1c5a53c025ad131a lunid: 0
                client iqn: iqn.1994-05.com.redhat:9f2838fc926e lun sn: 134587c046dae13e lunid: 1
```
`[root@ceph-2 ~]# tcpdump -n -i ens160 host 10.255.101.74 and 10.255.101.73 and port 3260`

- Initiator 认证要求：
    - 在initiator尝试连接到一个target的时候，initator需要提供一个用户名和密码给target供target进行认证。下面我们称这个用户名密码为incoming账号，即：`incoming账号`是initiator端提供给target端，供target端认证的账号。
- target 认证要求：
    - 在initiator尝试连接到一个target的时候，target需要提供一个用户名和密码给initiator供initiator进行认证。与之对应的是outcoming账号，即：`outcoming账号`是target端提供给initiator端，供initiator认证的账号。
- 对于一个target，可以绑定多个incoming账号，但是outgoing账号只能绑定一个。也就是说，对于不同initiator端，我们可以设置不同的incoming账号；但是所有的initiator端的outcoming账号必须是一致的。（以上结论只针对某个特定的target）。
- In computing, the Challenge-Handshake Authentication Protocol (CHAP) authenticates a user or network host to an authenticating entity. 
- The verification is based on a shared secret (such as the client's password).

![CHAP](https://github.com/microyahoo/robotframework_demo/blob/master/diagram/chap.png)

---
## 9. Mapping group
- TaskTypeUpdateMappingGroup
```
Request URL: http://10.255.101.73:8056/api/v1/mapping-groups/2/block-volumes?force=false
Request Method: DELETE
Request Payload:
    {block_volume_ids: [465]}
```
```
{
    "force": false,
    "access_path":  {
        id: <id>
    },
    "mapping_group": {
        id: <id>
    },
    removing_volume_ids: [1,2,3]
}
```
```
{
    "access_path":  {
        id: <id>
    },
    "mapping_group": {
        id: <id>
    },
    adding_volume_ids: [1,2,3]
}
```

---
## References:
- [iSCSI CHAP认证](https://www.cnblogs.com/jackydalong/archive/2013/04/28/3048748.html)
- [Linux tcpdump详解](https://www.cnblogs.com/ggjucheng/archive/2012/01/14/2322659.html)
- [CHAP wiki](https://en.wikipedia.org/wiki/Challenge-Handshake_Authentication_Protocol)