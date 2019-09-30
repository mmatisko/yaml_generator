from ipaddress import ip_address, ip_network
from random import getrandbits


class Network(object):
    def __init__(self, network_ip: str):
        self.network_ip = ''
        try:
            self.network_ip = ip_network(network_ip)
        except ValueError:
            print("Invalid network address arrived!")
        finally:
            print("Network has started...")

    def is_initialized(self) -> bool:
        return not self.network_ip == ''

    def get_random_ip(self) -> str:
        return str(self.get_random_ips(1))

    def get_random_ips(self, count: int) -> set:
        results: set = set()
        while len(results) < count:
            bits = getrandbits(self.network_ip.max_prefixlen - self.network_ip.prefixlen)
            addr = ip_address(self.network_ip.network_address + bits)
            results.add(str(addr))
        return results

    def is_address_in_network(self, address: str) -> bool:
        return ip_address(address) in self.network_ip

    def are_addresses_in_network(self, addresses: list) -> bool:
        for address in addresses:
            if not ip_address(address) in self.network_ip:
                return False
        return True
