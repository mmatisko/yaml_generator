from argparser import ArgumentType
from list_reader import ListFileReader
from network import Network
from portrange import PortRange


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


class DynamicTypeDetector(Singleton):
    def __init__(self):
        super(DynamicTypeDetector, self).__init__()

    # noinspection PyMethodMayBeStatic
    def is_type(self, type_init: classmethod, value: str) -> bool:
        try:
            return type_init(value).is_valid
        except ValueError:
            return False
        except Exception:
            raise

    def is_network(self, value: str) -> bool:
        try:
            return self.is_type(Network, value)
        except Exception:
            raise

    def is_port_range(self, value: str) -> bool:
        try:
            return self.is_type(PortRange, value)
        except Exception:
            raise

    def is_file(self, value: str) -> bool:
        try:
            return self.is_type(ListFileReader, value)
        except Exception:
            raise

    def detect_type(self, value: str) -> ArgumentType:
        pairs: dict[ArgumentType, object] = dict({
            ArgumentType.RandomPickFile: lambda item: self.is_file(item),
            ArgumentType.Network: lambda item: self.is_network(item),
            ArgumentType.PortRange: lambda item: self.is_port_range(item)
        })
        try:
            for value_type, fnc in pairs.items():
                if callable(fnc) and fnc(value):
                    return value_type
            raise InvalidDynamicValue
        except Exception:
            raise


class InvalidDynamicValue(Exception):
    @staticmethod
    def what():
        return "Invalid dynamic value provided in configure file!"
