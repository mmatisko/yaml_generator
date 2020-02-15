from enum import Enum
from network import Network
from portrange import PortRange


class DynamicValueType(Enum):
    Network = 0
    PortRange = 1
    File = 2


class DynamicTypeDetector(object):
    def __init__(self):
        pass

    @staticmethod
    def is_network(value: str) -> bool:
        try:
            net = Network(value)
            return net.is_valid()
        except ValueError:
            return False
        except Exception:
            raise

    @staticmethod
    def is_port(value: str) -> bool:
        try:
            port_range = PortRange(value)
            return port_range.is_valid()
        except ValueError:
            return False
        except Exception:
            raise

    @staticmethod
    def is_file(value: str) -> bool:
        pass

    @staticmethod
    def detect_type(value: str) -> DynamicValueType:
        try:
            if DynamicTypeDetector.is_network(value):
                return DynamicValueType.Network
            elif DynamicTypeDetector.is_port(value):
                return DynamicValueType.PortRange
            elif DynamicTypeDetector.is_file(value):
                return DynamicValueType.File
            else:
                raise InvalidDynamicValue

        except Exception:
            raise


class InvalidDynamicValue(Exception):
    @staticmethod
    def what():
        return "Invalid dynamic value provided in configure file!"
