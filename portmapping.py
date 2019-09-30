class PortMapping(object):
    def __init__(self, ports: str):
        self.port_mapping: dict = {}
        self.internal_ports, self.external_ports = self.parse_ports(ports)
        self.assign_ports_to_map(self.internal_ports, self.external_ports)

    def parse_ports(self, ports: str) -> [list, list]:
        split_ports = ports.split('/')
        if len(split_ports) != 2:
            raise ValueError
        internal_str_ports = split_ports[0]
        external_str_ports = split_ports[1]

        return self.convert_ports(internal_str_ports, external_str_ports)

    def convert_ports(self, internal_str_ports: str, external_str_ports: str) -> [list, list]:
        internal_ports: list = self.str_list_to_int_list(internal_str_ports, 1, 1023)
        external_ports: list = self.str_list_to_int_list(external_str_ports, 1024, 65535)
        return [internal_ports, external_ports]

    @staticmethod
    def str_list_to_int_list(str_ports: str, bottom_index: int, upper_index) -> list:
        int_ports = list()
        port_list: list = str_ports.split(',')
        for str_port in port_list:
            port = int(str_port)
            if port not in range(bottom_index, upper_index):
                raise ValueError
            else:
                int_ports.append(port)
        return int_ports

    @staticmethod
    def are_valid(internal_ports: list, external_ports: list) -> bool:
        if not len(internal_ports) == len(external_ports):
            return False
        for port in internal_ports:
            if not int(port) in range(1, 1023):
                return False
        for port in external_ports:
            if not int(port) in range(1024, 65535):
                return False
        return True

    def assign_ports_to_map(self, internal_ports, external_ports):
        while len(internal_ports) > 0:
            self.port_mapping[internal_ports.pop(0)] = external_ports.pop(0)

    def get_map(self):
        return self.port_mapping
