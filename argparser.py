from enum import Enum
import getopt
import sys


class ArgParser(object):
    def __init__(self):
        if __debug__:
            print("Arg Parse has started...")

    @staticmethod
    def parse(argv):
        try:
            opts, args = getopt.getopt(argv, "EHGc:d:f:i:n:p:v:")
        except getopt.GetoptError:
            raise ArgumentError

        params: dict = {ArgumentType.AppMode: AppMode.Unknown}

        for opt, arg in opts:
            if opt in ("-H", "--help"):
                print("main.py -d <dir> [-n <network> | -p <ports> | -f <file for random item pick>] ..for edit mode")
                print("main.py -d <dir> -c <config> ..for generate mode")
                sys.exit(1)
            if opt in ("-E", "--edit"):
                params[ArgumentType.AppMode] = AppMode.Edit
            if opt in ("-G", "--generate"):
                params[ArgumentType.AppMode] = AppMode.Generate

            if params[ArgumentType.AppMode] == AppMode.Generate or params[ArgumentType.AppMode] == AppMode.Edit:
                if opt in ("-c", "--config"):
                    params[ArgumentType.ConfigFile] = arg
                if opt in ("-d", "--dir"):
                    params[ArgumentType.AnsibleConfigDir] = arg

            if params[ArgumentType.AppMode] == AppMode.Edit:
                if opt in ("-i", "--item"):
                    params[ArgumentType.ItemKey] = arg
                if opt in ("-v", "--value"):
                    params[ArgumentType.ItemValue] = arg

                if opt in ("-n", "--network"):
                    params[ArgumentType.Network] = arg
                if opt in ("-p", "--ports"):
                    params[ArgumentType.PortRange] = arg
                if opt in ("-f", "--file"):
                    params[ArgumentType.RandomPickFile] = arg

            if params[ArgumentType.AppMode] == AppMode.Unknown:
                raise ArgumentModeError

        return params


class AppMode(Enum):
    Unknown = 0
    Edit = 1
    Generate = 2

    def __str__(self):
        return str(self.name)


class ArgumentType(Enum):
    AppMode = 1
    ConfigFile = 2
    AnsibleConfigDir = 3
    ItemKey = 4
    ItemValue = 5
    Network = 6
    PortRange = 7
    RandomPickFile = 8

    def __str__(self):
        return str(self.name)


class ArgumentError(getopt.GetoptError):
    @staticmethod
    def what():
        return "Invalid argument passed!"


class ArgumentModeError(getopt.GetoptError):
    @staticmethod
    def what():
        return "Invalid argument mode!"

# main.py 
# -n --network /network
# -p --ports /port mapping
# -c --config /external config linking
# -s --subnets /number of subnets
# -h --hosts /number of hosts in each subnet
# -H --help /print help 
#
# generate mode:
# main.py -n 192.168.10.0/24 -p 80,443 11180,11443 -s 1 -h 1
