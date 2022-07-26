#! /usr/bin/env python

import winrm

IP      = "10.0.11.125"
SCHEMA  = "http"
URL     = "{schema}://{ip}:{port}/wsman"
USER    = 'administrator' 
PWD     = '123.com'

class Client(object):
    def __init__(self, ip, username, password, port=5985):
        self._host      = ip 
        self._port      = port
        self._username  = username
        self._password  = password
        self._session   = winrm.Session(URL.format(schema=SCHEMA, ip=ip, port=port), auth=(username, password))

    def run_cmd(self, cmd, *args):
        return self._session.run_cmd(cmd, *args)

    def run_powershell(self, script):
        return self._session.run_ps(script)

if __name__ == "__main__":
    client = Client(ip=IP, username=USER, password=PWD)
    r = client.run_cmd('ipconfig', ['/all'])
    if r.status_code == 0:
        print r.std_out
    else:
        print r.std_err

    ps_script = """$strComputer = $Host
    Clear
    $RAM = WmiObject Win32_ComputerSystem
    $MB = 1048576

    "Installed Memory: " + [int]($RAM.TotalPhysicalMemory /$MB) + " MB" """

    r = client.run_powershell(ps_script)
    if r.status_code == 0:
        print r.std_out
    else:
        print r.std_err
