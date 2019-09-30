from argparse import ArgParse
from externalconfig import ExternalConfig
from logger import Logger
from network import Network
from portmapping import PortMapping

class tests(object):
    def __init__(self):
        print("Initializing tests...")

    def arg_parse_test(self):
        print("Arg Parse test started!")
        args = "-n 192.168.10.0/24 -p 80,443-11180,11443 -c config.yml -s 1 -h 1".split()
        arg_parser = ArgParse()
        network, ports, config, subnets, hosts = arg_parser.parse(args)

        assert network == "192.168.10.0/24", ("Invalid IP:" + network)
        assert ports == "80,443-11180,11443", ("Invalid ports:" + ports)
        assert config == "config.yml", ("Invalid config: " + config)
        assert subnets == "1", ("Invalid subnet count:" + subnets)
        assert hosts == "1", ("Invalid hosts count:" + hosts)
        
        print("Arg Parse test passed!")

    def logger_test(self):
        print("Logger test started!")

        loggerman = Logger()
        assert loggerman.get_debug_log("debug") == (loggerman.get_timestamp() + " [DEBUG]: debug")
        assert loggerman.get_warning_log("warning") == (loggerman.get_timestamp() + " [WARNING]: warning")
        assert loggerman.get_error_log("error") == (loggerman.get_timestamp() + " [ERROR]: error")
        assert loggerman.get_log("message") == (loggerman.get_timestamp() + " message")

        print("Logger test passed!")

    def network_test(self):
        print("Network test started!")

        network_tester = Network("192.168.10.0/24")
        assert network_tester.is_initialized()
        random_ip = network_tester.get_random_ip()
        assert len(random_ip) == 1
        random_ip = network_tester.get_random_ips(5)
        print(random_ip)
        assert len(network_tester.get_random_ips(5)) == 5
        assert network_tester.is_address_in_network("192.168.10.20")
        assert network_tester.are_addresses_in_network(["192.168.10.1","192.168.10.2"])
        assert not network_tester.is_address_in_network("192.168.15.15")

        network_tester = Network("192.168.256.255/32")
        assert not network_tester.is_initialized()

        network_tester = Network("192.168.255.0/33")
        assert not network_tester.is_initialized()

        network_tester = Network("192.168.255.255/24")
        assert not network_tester.is_initialized()

        print("Network test passed!")

    def external_config_test(self):
        print("External config test started!")

        external_cfg = ExternalConfig("config.yml")
        assert external_cfg.verify()
        assert external_cfg.get_path() == "config.yml"
        backup = external_cfg.get_rules()
        external_cfg.get_yaml_object().set_rules(backup)
        external_cfg.get_yaml_object().write()
        new = external_cfg.get_rules()
        #print('backup:' + str(backup))
        #print('new: ' + str(new))
        assert backup == new

        print("External config test passed!")

    def port_mapping_test(self):
        print("Port mapping test started!")

        port_mapping = PortMapping('80,443/11180,11443')
        assert port_mapping.are_valid([80,443],[11180,11443])
        test_mapping = {80: 11180, 443: 11443}
        assert port_mapping.get_map() == test_mapping

        print("Port mapping test passed!")

tester = tests()
tester.arg_parse_test()
tester.logger_test()
tester.network_test()
tester.external_config_test()
tester.port_mapping_test()

