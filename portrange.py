from dynamic_value import DynamicValue
from random import randint


class PortRange(DynamicValue):
    def __init__(self, ports: str):
        self.used_ports: set = set()
        self.range_begin: int = 0
        self.range_end: int = 0
        try:
            self.__parse_ports(ports)
        except Exception:
            raise

    def __parse_ports(self, ports: str):
        split_ports = ports.split('-')
        if len(split_ports) != 2:
            raise InvalidPortRangeException
        try:
            self.range_begin = int(split_ports[0])
            self.range_end = int(split_ports[1])
        except Exception:
            raise

    @property
    def is_valid(self) -> bool:
        return self.range_begin in range(1, 65535) \
            and self.range_end in range(1, 65535)  \
            and self.range_begin <= self.range_end

    def get_random_value(self) -> int:
        random_port: int = 0
        while random_port == 0 or random_port in self.used_ports:
            random_port = randint(self.range_begin, self.range_end)
        self.used_ports.add(random_port)
        return random_port


class InvalidPortRangeException(Exception):
    @staticmethod
    def what():
        return "Invalid port range provided!"
