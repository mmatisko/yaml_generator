from ansibledir import AnsibleDirectory
from argparser import ArgParser
from configuration import Configuration
from dynamic_value import DynamicValue
from list_reader import ListFileReader
from logger import Logger
from network import Network
from portrange import InvalidPortRangeException, PortRange
from type_detector import DynamicTypeDetector, DynamicValueType
from yamlio import YamlIo

import unittest


class UnitTest(unittest.TestCase):
    test_file: str = "/run/media/mmatisko/Data/Documents/FEKT/DP/program/include/testing/config.yml"
    test_dir: str = "./template_config/"

    def test_arg_parse_generate(self):
        args = ("-G -c " + UnitTest.test_file + " -d " + UnitTest.test_dir).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params['mode'], "generate", ("Invalid mode: " + params['mode']))
        self.assertEqual(params['config'], UnitTest.test_file, ("Invalid config: " + params['config']))
        self.assertEqual(params['dir'], UnitTest.test_dir, ("Invalid template directory:" + params['dir']))

    def test_arg_parse_edit(self):
        args = "-E -i mysql_port -v 3336 -c config.yml".split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params['mode'], "edit", ("Invalid mode: " + params['mode']))
        self.assertEqual(params['item'], "mysql_port", ("Invalid item: " + params['item']))
        self.assertEqual(params['value'], "3336", ("Invalid value: " + params['value']))
        self.assertEqual(params['config'], "config.yml", ("Invalid config: " + params['config']))

    def test_logger(self):
        my_py_log = Logger()
        self.assertEqual(my_py_log.get_debug_log("debug"), (my_py_log.get_timestamp() + " [DEBUG]: debug"))
        self.assertEqual(my_py_log.get_warning_log("warning"), (my_py_log.get_timestamp() + " [WARNING]: warning"))
        self.assertEqual(my_py_log.get_error_log("error"), (my_py_log.get_timestamp() + " [ERROR]: error"))
        self.assertEqual(my_py_log.get_log("message"), (my_py_log.get_timestamp() + " message"))

    def test_network(self):
        network_tester = Network("192.168.10.128/25")
        self.assertTrue(network_tester.is_valid)
        random_ip = network_tester.get_random_value()
        self.assertEqual(len(random_ip), 14)
        random_ips = network_tester.get_random_values(5)
        if __debug__:
            print(random_ip)
        self.assertEqual(len(random_ips), 5)
        self.assertTrue(network_tester.is_address_in_network("192.168.10.220"))
        self.assertTrue(network_tester.is_address_in_network("192.168.10.221"))
        self.assertFalse(network_tester.is_address_in_network("192.168.10.15"))
        self.assertFalse(network_tester.is_address_in_network("172.16.150.220"))

        self.assertRaises(ValueError, Network, "192.168.256.255/32")
        self.assertRaises(ValueError, Network, "192.168.255.0/33")
        self.assertRaises(ValueError, Network, "192.168.255.255/24")

    def test_external_config(self):
        external_cfg = Configuration(UnitTest.test_file)
        self.assertTrue(external_cfg.is_valid())
        self.assertEqual(external_cfg.get_path(), UnitTest.test_file, ("Invalid path: " + external_cfg.get_path()))
        external_cfg.read_rules()
        item = "foo"
        backup_value = external_cfg.get_value(item)
        external_cfg.set_rules()
        external_cfg.read_rules()
        new_value = external_cfg.get_value(item)
        self.assertEqual(new_value, backup_value, ("Invalid new value: " + new_value))

    def test_port_range(self):
        # invalid port ranges
        port_ranges: list = [PortRange('0-1'), PortRange('100-10'), PortRange('5-66000')]
        for port_range in port_ranges:
            self.assertFalse(port_range.is_valid)
        with self.assertRaises(InvalidPortRangeException):
            _ = PortRange('1-2-3')
        with self.assertRaises(InvalidPortRangeException):
            _ = PortRange('80')
        # valid port range
        port_range = PortRange('80-443')
        self.assertTrue(port_range.is_valid)
        self.assertTrue(port_range.get_random_value() in range(80, 444))
        # single valid port
        http_only_port_range = PortRange('80-80')
        self.assertTrue(http_only_port_range.is_valid)
        self.assertEqual(http_only_port_range.get_random_value(), 80)

    def test_file_edit_str_item(self):
        args = ("-E -i foo -v barbar -c " + UnitTest.test_file).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertTrue(YamlIo.is_valid(params['config']), "Config file is invalid!")
        cfg = Configuration(params['config'])
        cfg.read_rules()
        cfg.set_value(params['item'], params['value'])
        cfg.set_rules()

        self.assertTrue(cfg.key_exists(params['item']), ("Item " + params['item'] + " do not exists in " +
                                                         UnitTest.test_file + "!"))
        configured_value = cfg.get_value(params['item'])
        self.assertEqual(configured_value, params['value'])

    def test_file_edit_generated_ip(self):
        args = ("-E -i ip -n 192.168.100.0/25 -c " + UnitTest.test_file).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        ip = Network(params['network']).get_random_value()

        cfg = Configuration(params['config'])
        cfg.read_rules()
        cfg.set_value(params['item'], ip)
        cfg.set_rules()
        cfg.write_rules(UnitTest.test_file)

        cfg.read_rules()
        self.assertEqual(ip, cfg.get_value(params['item']))

    def test_ansible_dir_count(self):
        args = "-E -d /run/media/mmatisko/Data/Documents/FEKT/DP/program/include/lamp_simple/ -i foo -v barbar".split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)
        ans_dir = AnsibleDirectory(params['dir'])
        if __debug__:
            ans_dir.iterate_directory_tree(lambda filename: print(filename.name))
        else:
            ans_dir.iterate_directory_tree(lambda _: None)
        result: int = ans_dir.count_files_in_tree()
        self.assertEqual(result, 15, ("Invalid files number: " + str(result)))

    def test_dynamic_types_interface(self):
        self.assertTrue(issubclass(PortRange, DynamicValue))
        self.assertTrue(issubclass(Network, DynamicValue))
        self.assertTrue(issubclass(ListFileReader, DynamicValue))

    def test_type_detection(self):
        detector = DynamicTypeDetector()

        valid_net: str = '192.168.10.0/24'
        self.assertTrue(detector.is_network(valid_net))
        self.assertEqual(detector.detect_type(valid_net), DynamicValueType.Network)

        valid_port: str = '1011-1012'
        self.assertTrue(detector.is_port(valid_port))
        self.assertEqual(detector.detect_type(valid_port), DynamicValueType.PortRange)

        invalid_port: str = '80'
        with self.assertRaises(InvalidPortRangeException):
            _ = detector.detect_type(invalid_port)

        invalid_network: str = '192.156.156.256/33'
        with self.assertRaises(InvalidPortRangeException):
            _ = detector.detect_type(invalid_network)

    def test_simple_text_detection_read(self):
        detector = DynamicTypeDetector()
        valid_file: str = './include/passwords.txt'
        self.assertEqual(detector.detect_type(valid_file), DynamicValueType.File)

        reader = ListFileReader(valid_file)
        self.assertEqual(reader.reader.get_item_count(), 7)
        self.assertEqual(reader.reader.read_value(6), 'heslopass')
        self.assertTrue(reader.get_random_value() in {'heslo', 'heslo1', 'heslo2', 'password',
                                                      'heslo123', 'pass12345', 'heslopass'})

    def test_csv_detection_read(self):
        detector = DynamicTypeDetector()
        valid_file: str = './include/logins.csv'
        self.assertEqual(detector.detect_type(valid_file), DynamicValueType.File)

        reader = ListFileReader(valid_file)
        self.assertEqual(reader.reader.get_item_count(), 6)
        self.assertEqual(reader.reader.read_value(0), 'username')
        self.assertEqual(reader.reader.read_value(2), 'user')
        self.assertEqual(reader.reader.read_value(4), 'visible_login')
        self.assertEqual(reader.reader.read_value(5), 'last_login')
        self.assertTrue(reader.get_random_value() in {'username', 'login', 'user', 'login_name',
                                                      'visible_login', 'last_login'})

    def test_input_config(self):
        config = Configuration('./include/generator_config.yml')
        self.assertTrue(config.is_valid())

        config.read_rules()
        self.assertTrue(config.key_exists('general'))
        self.assertTrue(config.key_exists('static'))
        self.assertTrue(config.key_exists('dynamic'))
        self.assertTrue(config.key_exists('iterations'))


if __name__ == '__main__':
    unittest.main()