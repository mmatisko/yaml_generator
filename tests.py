from ansibledir import AnsibleDirectory
from argparse import ArgParse
from configuration import Configuration
from logger import Logger
from network import Network
from portmapping import PortMapping
from yamlio import YamlIo


class Tests(object):
    test_file: str = "/run/media/mmatisko/Data/Documents/FEKT/DP/program/include/config.yml"

    def __init__(self):
        print("Initializing tests...")

    @staticmethod
    def arg_parse_generate_test():
        print("Arg Parse generate mode test started!")
        args = ("-G -n 192.168.10.0/24 -p 80,443-11180,11443 -c " + Tests.test_file + " -s 1 -h 1").split()
        arg_parser = ArgParse()
        params = arg_parser.parse(args)

        assert params['mode'] == "generate", ("Invalid mode: " + params['mode'])
        assert params['network'] == "192.168.10.0/24", ("Invalid IP:" + params['network'])
        assert params['ports'] == "80,443-11180,11443", ("Invalid ports:" + params['ports'])
        assert params['config'] == Tests.test_file, ("Invalid config: " + params['config'])
        assert params['subnets'] == "1", ("Invalid subnet count:" + params['subnets'])
        assert params['hosts'] == "1", ("Invalid hosts count:" + params['hosts'])

        print("Arg Parse generate mode test passed!")

    @staticmethod
    def arg_parse_replace_test():
        print("Arg Parse replace mode test started!")
        args = "-R -k mysql_port -v 3336 -c config.yml".split()
        arg_parser = ArgParse()
        params = arg_parser.parse(args)

        assert params['mode'] == "replace", ("Invalid mode: " + params['mode'])
        assert params['key'] == "mysql_port", ("Invalid key: " + params['key'])
        assert params['value'] == "3336", ("Invalid value: " + params['value'])
        assert params['config'] == "config.yml", ("Invalid config: " + params['config'])

    @staticmethod
    def logger_test():
        print("Logger test started!")

        loggerman = Logger()
        assert loggerman.get_debug_log("debug") == (loggerman.get_timestamp() + " [DEBUG]: debug")
        assert loggerman.get_warning_log("warning") == (loggerman.get_timestamp() + " [WARNING]: warning")
        assert loggerman.get_error_log("error") == (loggerman.get_timestamp() + " [ERROR]: error")
        assert loggerman.get_log("message") == (loggerman.get_timestamp() + " message")

        print("Logger test passed!")

    @staticmethod
    def network_test():
        print("Network test started!")

        network_tester = Network("192.168.10.128/25")
        assert network_tester.is_initialized()
        random_ip = network_tester.get_random_ip()
        assert len(random_ip) == 14
        random_ip = network_tester.get_random_ips(5)
        print(random_ip)
        assert len(network_tester.get_random_ips(5)) == 5
        assert network_tester.is_address_in_network("192.168.10.220")
        assert network_tester.are_addresses_in_network(["192.168.10.221", "192.168.10.254"])
        assert not network_tester.is_address_in_network("192.168.10.15")
        assert not network_tester.is_address_in_network("172.16.150.220")

        network_tester = Network("192.168.256.255/32")
        assert not network_tester.is_initialized()

        network_tester = Network("192.168.255.0/33")
        assert not network_tester.is_initialized()

        network_tester = Network("192.168.255.255/24")
        assert not network_tester.is_initialized()

        print("Network test passed!")

    @staticmethod
    def external_config_test():
        print("External config test started!")

        external_cfg = Configuration(Tests.test_file)
        assert external_cfg.verify()
        assert external_cfg.get_path() == Tests.test_file, ("Invalid path: " + external_cfg.get_path())
        external_cfg.read_rules()
        key = "foo"
        backup_value = external_cfg.get_value(key)
        external_cfg.set_rules()
        external_cfg.read_rules()
        new_value = external_cfg.get_value(key)
        assert new_value == backup_value, ("Invalid new value: " + new_value)

        print("External config test passed!")

    @staticmethod
    def port_mapping_test():
        print("Port mapping test started!")

        port_mapping = PortMapping('80,443/11180,11443')
        assert port_mapping.are_valid([80, 443], [11180, 11443])
        test_mapping = {80: 11180, 443: 11443}
        assert port_mapping.get_map() == test_mapping

        print("Port mapping test passed!")

    @staticmethod
    def test_file_replace_test():
        print('Test file replace test started!')

        args = ("-R -k foo -v barbar -c " + Tests.test_file).split()
        arg_parser = ArgParse()
        params = arg_parser.parse(args)

        assert YamlIo.is_valid(params['config']), "Config file is invalid!"
        cfg = Configuration(params['config'])
        cfg.read_rules()
        cfg.set_value(params['key'], params['value'])
        cfg.set_rules()

        assert cfg.key_exists(params['key']), ("Key " + params['key'] + " do not exists in " + Tests.test_file + "!")
        configured_value = cfg.get_value(params['key'])
        assert configured_value == params['value']
        print("Test file replace passed!")

    @staticmethod
    def ansible_dir_count_test():
        ans_dir = AnsibleDirectory('/run/media/mmatisko/Data/Documents/FEKT/DP/program/include/lamp_simple/')
        ans_dir.iterate_directory_tree(lambda filename: print(filename.name))
        result: int = ans_dir.count_files_in_tree()
        assert result == 15, ("Invalid files number: " + str(result))


# run all tests:
tests = Tests()
functions = [func for func in dir(tests) if callable(getattr(tests, func)) and not func.startswith('__')]
for func in functions:
    callable_func = getattr(tests, func)
    callable_func()
