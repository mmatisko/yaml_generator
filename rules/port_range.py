"""
Represents Port range class, verify input value and construct object if input is valid,
object is able to generate random values from range.
"""

from .crypto_random import CryptoRandom
from .dynamic_value import DynamicValue


class PortRange(DynamicValue):
    def __init__(self, ports: str):
        self.__used_ports: set = set()
        self.__range_begin: int = 0
        self.__range_end: int = 0
        try:
            self.__parse_ports(ports)
        except Exception:
            raise

    def __parse_ports(self, ports: str):
        if not ports[0].isdigit():
            raise ValueError("Not a port range")
        split_ports = ports.split('-')
        if len(split_ports) != 2:
            raise InvalidPortRangeException
        try:
            self.__range_begin = int(split_ports[0])
            self.__range_end = int(split_ports[1])
        except Exception:
            raise

    @property
    def is_valid(self) -> bool:
        return self.__range_begin in range(1, 65535) \
               and self.__range_end in range(1, 65535) \
               and self.__range_begin <= self.__range_end

    def get_random_value(self) -> int:
        random_port: int = 0
        while random_port == 0 or random_port in self.__used_ports:
            random_port = CryptoRandom.random_int(self.__range_begin, self.__range_end)
        self.__used_ports.add(random_port)
        return random_port

    def clear_used_values(self):
        self.__used_ports.clear()


class InvalidPortRangeException(Exception):
    @staticmethod
    def what():
        return "Invalid port range provided!"
