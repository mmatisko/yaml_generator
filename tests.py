from ansibledir import AnsibleDirectory
from argparser import ArgParser
from configuration import Configuration
from logger import Logger
from network import Network
from portmapping import PortMapping
from yamlio import YamlIo

import unittest


class Tests(unittest.TestCase):
    test_file: str = "/run/media/mmatisko/Data/Documents/FEKT/DP/program/include/testing/config.yml"

    def test_arg_parse_generate(self):
        args = ("-G -n 192.168.10.0/24 -p 80,443-11180,11443 -c " + Tests.test_file + " -s 1 -h 1").split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params['mode'], "generate", ("Invalid mode: " + params['mode']))
        self.assertEqual(params['network'], "192.168.10.0/24", ("Invalid IP:" + params['network']))
        self.assertEqual(params['ports'], "80,443-11180,11443", ("Invalid ports:" + params['ports']))
        self.assertEqual(params['config'], Tests.test_file, ("Invalid config: " + params['config']))
        self.assertEqual(params['subnets'], "1", ("Invalid subnet count:" + params['subnets']))
        self.assertEqual(params['hosts'], "1", ("Invalid hosts count:" + params['hosts']))

    def test_arg_parse_replace(self):
        args = "-R -i mysql_port -v 3336 -c config.yml".split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params['mode'], "replace", ("Invalid mode: " + params['mode']))
        self.assertEqual(params['item'], "mysql_port", ("Invalid item: " + params['item']))
        self.assertEqual(params['value'], "3336", ("Invalid value: " + params['value']))
        self.assertEqual(params['config'], "config.yml", ("Invalid config: " + params['config']))

    def test_logger(self):
        loggerman = Logger()
        self.assertEqual(loggerman.get_debug_log("debug"), (loggerman.get_timestamp() + " [DEBUG]: debug"))
        self.assertEqual(loggerman.get_warning_log("warning"), (loggerman.get_timestamp() + " [WARNING]: warning"))
        self.assertEqual(loggerman.get_error_log("error"), (loggerman.get_timestamp() + " [ERROR]: error"))
        self.assertEqual(loggerman.get_log("message"), (loggerman.get_timestamp() + " message"))

    def test_network(self):
        network_tester = Network("192.168.10.128/25")
        self.assertTrue(network_tester.is_initialized())
        random_ip = network_tester.get_random_ip()
        self.assertEqual(len(random_ip), 14)
        random_ips = network_tester.get_random_ips(5)
        if __debug__:
            print(random_ip)
        self.assertEqual(len(random_ips), 5)
        self.assertTrue(network_tester.is_address_in_network("192.168.10.220"))
        self.assertTrue(network_tester.are_addresses_in_network(["192.168.10.221", "192.168.10.254"]))
        self.assertFalse(network_tester.is_address_in_network("192.168.10.15"))
        self.assertFalse(network_tester.is_address_in_network("172.16.150.220"))

        self.assertRaises(ValueError, Network, "192.168.256.255/32")
        self.assertRaises(ValueError, Network, "192.168.255.0/33")
        self.assertRaises(ValueError, Network, "192.168.255.255/24")

    def test_external_config(self):
        external_cfg = Configuration(Tests.test_file)
        self.assertTrue(external_cfg.verify())
        self.assertEqual(external_cfg.get_path(), Tests.test_file, ("Invalid path: " + external_cfg.get_path()))
        external_cfg.read_rules()
        item = "foo"
        backup_value = external_cfg.get_value(item)
        external_cfg.set_rules()
        external_cfg.read_rules()
        new_value = external_cfg.get_value(item)
        self.assertEqual(new_value, backup_value, ("Invalid new value: " + new_value))

    def test_port_mapping(self):
        port_mapping = PortMapping('80,443/11180,11443')
        self.assertTrue(port_mapping.are_valid([80, 443], [11180, 11443]))
        test_mapping = {80: 11180, 443: 11443}
        self.assertEqual(port_mapping.get_map(), test_mapping)

    def test_file_replace_str_item(self):
        args = ("-R -i foo -v barbar -c " + Tests.test_file).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertTrue(YamlIo.is_valid(params['config']), "Config file is invalid!")
        cfg = Configuration(params['config'])
        cfg.read_rules()
        cfg.set_value(params['item'], params['value'])
        cfg.set_rules()

        self.assertTrue(cfg.key_exists(params['item']), ("Item " + params['item'] + " do not exists in " +
                                                         Tests.test_file + "!"))
        configured_value = cfg.get_value(params['item'])
        self.assertEqual(configured_value, params['value'])

    def test_file_replace_generated_ip(self):
        args = ("-G -i ip -n 192.168.100.0/25 -c " + Tests.test_file).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        ip = Network(params['network']).get_random_ip()

        cfg = Configuration(params['config'])
        cfg.read_rules()
        cfg.set_value(params['item'], ip)
        cfg.set_rules()
        cfg.write_rules(Tests.test_file)

        cfg.read_rules()
        self.assertEqual(ip, cfg.get_value(params['item']))

    def test_ansible_dir_count(self):
        args = "-R -d /run/media/mmatisko/Data/Documents/FEKT/DP/program/include/lamp_simple/ -i foo -v barbar".split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)
        ans_dir = AnsibleDirectory(params['dir'])
        if __debug__:
            ans_dir.iterate_directory_tree(lambda filename: print(filename.name))
        else:
            ans_dir.iterate_directory_tree(lambda param: None)
        result: int = ans_dir.count_files_in_tree()
        self.assertEqual(result, 15, ("Invalid files number: " + str(result)))


if __name__ == '__main__':
    unittest.main()
