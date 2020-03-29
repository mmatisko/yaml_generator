from enum import Enum
import getopt
import sys


class ArgParser(object):
    @staticmethod
    def parse(argv):
        try:
            opts, args = getopt.getopt(argv, "EHGc:d:f:k:n:p:v:")
        except getopt.GetoptError:
            raise ArgumentError

        params: dict = {ArgumentType.AppMode: AppMode.Unknown}

        for opt, arg in opts:
            if opt in ("-H", "--help"):
                print("main.py -d <dir> -k <key> [-n <network> | -p <ports> | -f <file for random item pick>] "
                      "..for edit mode")
                print("main.py -d <dir> -c <config> ..for generate mode")
                sys.exit(1)
            if opt in ("-E", "--edit"):
                params[ArgumentType.AppMode] = AppMode.Edit
            if opt in ("-G", "--generate"):
                params[ArgumentType.AppMode] = AppMode.Generate

            if params[ArgumentType.AppMode] in [AppMode.Generate, AppMode.Edit]:
                if opt in ("-d", "--dir"):
                    params[ArgumentType.AnsibleConfigDir] = arg

            if params[ArgumentType.AppMode] == AppMode.Edit:
                if opt in ("-k", "--key"):
                    params[ArgumentType.ItemKey] = arg
                if opt in ("-v", "--value"):
                    params[ArgumentType.ItemValue] = arg

                if opt in ("-n", "--network"):
                    params[ArgumentType.Network] = arg
                if opt in ("-p", "--ports"):
                    params[ArgumentType.PortRange] = arg
                if opt in ("-f", "--file"):
                    params[ArgumentType.RandomPickFile] = arg

            if params[ArgumentType.AppMode] == AppMode.Generate:
                if opt in ("-c", "--config"):
                    params[ArgumentType.ConfigFile] = arg
                if opt in ("-o", "--output"):
                    params[ArgumentType.OutputFolder] = arg

            if params[ArgumentType.AppMode] == AppMode.Unknown:
                raise ArgumentModeError

        return params

    @staticmethod
    def params_are_valid(params: dict) -> bool:
        if params[ArgumentType.AppMode] is AppMode.Generate:
            return len(params.keys()) in range(2, 4) \
                   and ArgumentType.ConfigFile in params.keys() \
                   or ((len(params.keys()) is 3) and ArgumentType.AnsibleConfigDir in params.keys())
        elif params[ArgumentType.AppMode] is AppMode.Edit:
            return len(params.keys()) is 4 \
                   and ArgumentType.AnsibleConfigDir in params.keys()\
                   and ArgumentType.ItemKey in params.keys() \
                   and (ArgumentType.RandomPickFile in params.keys()
                        or ArgumentType.Network in params.keys()
                        or ArgumentType.PortRange in params.keys()
                        or ArgumentType.ItemValue in params.keys())
        else:
            return False


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
    OutputFolder = 9

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
