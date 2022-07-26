#! /usr/bin/env python

import argparse
import os
import sys
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from utils import run_command

# Refer to [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#module-search-path]
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

# TODO
class TestRunner(object):
    def __init__(self, argv):
        self.argv = argv
        self.opts = self.get_options()

    def get_options(self):
        parser = argparse.ArgumentParser(description="script for test runner")
        subparsers = parser.add_subparsers(help="TestRunner Commands", dest="_level")

        _robot_par = subprocess.add_parser("robot", help="robot file")

        _robot_file_par = _robot_par.add_subparsers(dest="subcommand", help="sub command of robot")
        _robot_file_par.add_argument("--file", metavar="file", required=True, help="robot file path")
        return parser.parse_args(self.argv)

def get_env_files(path='env/', ignore_pattern=".", suffix=None):
    """
    return all the env files accroding to sepecified path
    """
    if type(path) not in (str, unicode) or not os.path.exists(path):
        print("[Error] The path is invalid")
        return 
    file_list = []
    if os.path.isfile(path) and not path.startswith(ignore_pattern): 
        if suffix is None or suffix is not None and path.endswith(suffix):
            file_list.append(path)
    elif os.path.isdir(path):
        for s in os.listdir(path.decode('utf-8')):
            if not s.startswith(ignore_pattern):
                file_list.extend(get_env_files(os.path.join(path, s), 
                    ignore_pattern, suffix))

    return file_list

def load_env_files(files):
    envs = dict()
    if type(files) not in (list,) or len(files) == 0:
        print("[Error] The format of parameter is invalid, or the file list is\
              null")
        return
    try:
        for f in files:
            for key, val in yaml.load(file(f, 'r')).items():
                # os.environ["ENV_" + str(key).upper()] = str(val)
                envs["ENV_" + str(key).upper()] = str(val)
    except Exception as e:
        print("[Error] Failed to open file or the yaml file contains 'list':\
              [%s], %s" %(str(f), e.message))
    return envs

def run_test_cases(robot_file, env=None):
    cmd = "robot {robotfile}".format(robotfile=robot_file) 
    env_var = dict()
    #env_var.update(os.environ)
    if env is not None and type(env) in (dict,):
        env_var = dict(env)
    return run_command(cmd, environ_update=env_var)


# TODO
def main(argv):
    try:
        runner = TestRunner(argv)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    #path = "/Users/xsky/robot_test"
    #path = "/Users/xsky/robot_test/robotframework_demo/env"
    # path = "/Users/xsky/robot_test/robotframework_demo/"
    # files = get_env_files(path)
    #files = get_env_files(path, suffix="yaml")
    files = get_env_files(suffix="yaml")
    if files is None:
        print("[Info] You need to run the test cases in robot root path.")
        sys.exit(-1)
    envs = load_env_files(files)
    if len(sys.argv) > 1:
        print(run_test_cases(sys.argv[1], envs))


