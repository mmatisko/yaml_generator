from dynamic_value import DynamicValue
from ipaddress import ip_address, ip_network
from random import getrandbits


class Network(DynamicValue):
    def __init__(self, network_ip: str):
        self.network_ip = None
        try:
            self.network_ip = ip_network(network_ip)
        except ValueError:
            raise

    @property
    def is_valid(self) -> bool:
        return self.network_ip is not None

    def get_random_value(self) -> str:
        random_ip = str(self.get_random_values(1))
        return random_ip[2:len(random_ip)-2]

    def get_random_values(self, count: int) -> set:
        results: set = set()
        while len(results) < count:
            bits = getrandbits(self.network_ip.max_prefixlen - self.network_ip.prefixlen)
            addr = ip_address(self.network_ip.network_address + bits)
            results.add(str(addr))
        return results

    def is_address_in_network(self, address: str) -> bool:
        return ip_address(address) in self.network_ip
