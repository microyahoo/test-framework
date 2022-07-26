Robot Framework Demo
=================================

You can execute the command of "Test_Runner.py test_cases/test.robot" to run test cases.

```
File Hierarchy
.
├── README.md
├── Test_Runner.py
├── env
│   ├── bj
│   │   └── bj.yaml
│   ├── common.yaml
│   └── sz
│       └── sz.yaml
├── lib
│   ├── AccessPath.py
│   ├── Block.py
│   ├── BlockVolume.py
│   ├── ClientGroup.py
│   ├── Host.py
│   ├── IssueCmd.py
│   ├── MappingGroup.py
│   ├── Pool.py
│   ├── Snapshot.py
│   ├── TeardownBlock.py
│   └── utils.py
├── resources
│   └── ssh.robot
└── test_cases
    ├── example.robot
    └── test_block.robot
```

## References
  * [Robot Framework][ref-1]
  * [Robot Framework User Guide][ref-2]
  * [SSHLibrary][ref-3]
  * [Robot Framework Quick Start Guide][ref-4]
  * [SSHLibrary keywords][ref-5]
  * [virtualenv][ref-6]
  * [virtualenv User Guide][ref-7]
  * [Paramiko Exceptions][ref-8]
  * [Paramiko SSHClient][ref-9]
  * [ImportError: No module named ssl_match_hostname][ref-10]

[ref-1]: http://robotframework.org
[ref-2]: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html
[ref-3]: https://github.com/robotframework/SSHLibrary
[ref-4]: https://github.com/robotframework/QuickStartGuide/blob/master/QuickStart.rst
[ref-5]: http://robotframework.org/SSHLibrary/SSHLibrary.html
[ref-6]: https://pypi.org/project/virtualenv/
[ref-7]: https://virtualenv.pypa.io/en/stable/userguide/
[ref-8]: http://docs.paramiko.org/en/2.4/api/ssh_exception.html#
[ref-9]: http://docs.paramiko.org/en/1.15/api/client.html#paramiko.client.SSHClient.connect
[ref-10]: https://stackoverflow.com/questions/42695004/importerror-no-module-named-ssl-match-hostname-when-importing-the-docker-sdk-fo
