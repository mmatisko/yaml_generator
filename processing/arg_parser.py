"""
Argument parser used for parsing input arguments from CLI, checks all arguments, validate their count and fill
arguments dictionary with these values, which are used in generator. Option -H or --help prints out argument manual.
"""

from enum import Enum
import getopt
import sys


class ArgParser(object):
    @staticmethod
    def parse(argv):
        try:
            opts, args = getopt.getopt(argv, "ehgc:d:f:k:n:o:p:v:", ["help", "edit", "generate", "dir=",
                                                                     "key=", "value=", "network=", "ports=", "file=",
                                                                     "config=", "output="])
        except getopt.GetoptError:
            raise ArgumentError

        params: dict = {ArgumentType.AppMode: AppMode.Unknown}

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                ArgParser.__print_help()
                sys.exit(1)
            if opt in ("-e", "--edit"):
                params[ArgumentType.AppMode] = AppMode.Edit
            if opt in ("-g", "--generate"):
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
            return len(params.keys()) in range(2, 5) \
                   and ArgumentType.ConfigFile in params.keys()
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

    @staticmethod
    def __print_help():
        print("Editor mode usage: ans_gen.py -E -d <dir> -k <key> {-n | -p | -f | -v} <value>")
        print("Generator mode usage: ans_gen.py -G -c <config> [-d <value >| o <value>]")
        print("")
        print("Mode parameters (required):")
        print("-E, [--edit]  - editor mode, editing selected configuration folder")
        print("-G, [--generate]  - generator mode, generate new configurations")
        print("")
        print("Arguments valid in both modes:")
        print("-d, [--dir=],  - source directory of input config, optional in generator mode")
        print("")
        print("Arguments valid only in Editor mode:")
        print("-k, [--key=]  - name of item/rule, required argument with one of above")
        print("-v, [--value=]  - new static value of item")
        print("-n, [--network=]  - network value to generate item value")
        print("-p, [--ports=]  - port range to generate item value")
        print("-f, [--file=]  - source text file with list of item values")
        print("")
        print("Arguments valid only in Generator mode:")
        print("-c, [--config=]  - required, path of configuration file")
        print("-o, [--output=]  - optional, root path of generated configurations")


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
