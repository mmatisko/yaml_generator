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
            opts, args = getopt.getopt(argv, "HRGc:d:h:i:n:p:s:v:")
        except getopt.GetoptError:
            raise ArgumentError

        class AppMode(Enum):
            Unknown = 0
            Replace = 1
            Generate = 2
        mode: AppMode = AppMode.Unknown
        params: dict = {}

        for opt, arg in opts:
            if opt in ("-H", "--help"):
                print("main.py -n <network> -p <ports> -c <config> -s <subnet count> -h <hosts for subnets>")
                sys.exit(1)
            if opt in ("-R", "--replace"):
                params['mode'] = "replace"
                mode = AppMode.Replace
            if opt in ("-G", "--generate"):
                params['mode'] = "generate"
                mode = AppMode.Generate

            if mode == AppMode.Generate or mode == AppMode.Replace:
                if opt in ("-c", "--config"):
                    params['config'] = arg
                if opt in ("-d", "--dir"):
                    params['dir'] = arg
                if opt in ("-i", "--item"):
                    params['item'] = arg

            if mode == AppMode.Generate:
                if opt in ("-n", "--network"):
                    params['network'] = arg
                if opt in ("-p", "--ports"):
                    params['ports'] = arg
                if opt in ("-s", "--subnets"):
                    params['subnets'] = arg
                if opt in ("-h", "--hosts"):
                    params['hosts'] = arg

            if mode == AppMode.Replace:
                if opt in ("-v", "--value"):
                    params['value'] = arg

            if mode == AppMode.Unknown:
                raise ArgumentModeError

        return params


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