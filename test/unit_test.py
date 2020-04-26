"""
UnitTest for testing single methods and most important modules of generator.
"""

from file_io import AnsibleDirectory, FileVault, Logger, is_vault_file
from processing import AppMode, ArgParser, ArgumentType, Configuration
from rules import DynamicTypeDetector, DynamicValue, IteratorRegex, ListFileReader, InvalidPortRangeException, \
    Network, PortRange

import io
import os.path
import shutil
import unittest


class UnitTest(unittest.TestCase):
    __root_folder: str = '..'
    __test_file: str = os.path.join(__root_folder, 'include', 'test', 'config', 'config.yml')
    __test_file_dir: str = os.path.join(__root_folder, 'include', 'test', 'config')
    __non_existing_test_dir: str = os.path.join(__root_folder, 'not_existing_folder')

    """
    Test for parsing generator mode arguments.
    """
    def test_arg_parse_generate(self):
        args = ("-G -c " + UnitTest.__test_file + " -d " + UnitTest.__non_existing_test_dir).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params[ArgumentType.AppMode], AppMode.Generate, 
                         ("Invalid mode: " + str(params[ArgumentType.AppMode])))
        self.assertEqual(params[ArgumentType.ConfigFile], UnitTest.__test_file,
                         ("Invalid config: " + params[ArgumentType.ConfigFile]))
        self.assertEqual(params[ArgumentType.AnsibleConfigDir], UnitTest.__non_existing_test_dir,
                         ("Invalid Ansible directory:" + params[ArgumentType.AnsibleConfigDir]))

    """
    Test for parsing editor mode arguments.
    """
    def test_arg_parse_edit(self):
        args = '-E -k mysql_port -v 3336'.split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        self.assertEqual(params[ArgumentType.AppMode], AppMode.Edit, ("Invalid mode: " +
                                                                      str(params[ArgumentType.AppMode])))
        self.assertEqual(params[ArgumentType.ItemKey], "mysql_port", ("Invalid item: " + params[ArgumentType.ItemKey]))
        self.assertEqual(params[ArgumentType.ItemValue], "3336", ("Invalid value: " + params[ArgumentType.ItemValue]))

    """
    Test for logger class, writes message using all logging methods.
    """
    def test_logger(self):
        with io.StringIO() as reader:
            Logger.write_debug_log("debug", reader)
            self.assertTrue(reader.getvalue().rstrip().endswith(" [DEBUG]: debug"))

        with io.StringIO() as reader:
            Logger.write_warning_log("warning", reader)
            self.assertTrue(reader.getvalue().rstrip().endswith(" [WARNING]: warning"))

        with io.StringIO() as reader:
            Logger.write_error_log("error", reader)
            self.assertTrue(reader.getvalue().rstrip().endswith(" [ERROR]: error"))

        with io.StringIO() as reader:
            Logger.write_log("message", reader)
            self.assertTrue(reader.getvalue().rstrip().endswith(" message"))

    """
    Test for generating IP address from network address, check for invalid network addresses.
    """
    def test_network(self):
        network_tester = Network('192.168.10.128/25')
        self.assertTrue(network_tester.is_valid)
        random_ip = network_tester.get_random_value()
        self.assertEqual(len(random_ip), 14)
        random_ips = network_tester.get_random_values(5)
        if __debug__:
            print(random_ip)
        self.assertEqual(len(random_ips), 5)
        self.assertTrue(network_tester.is_address_in_network('192.168.10.220'))
        self.assertTrue(network_tester.is_address_in_network('192.168.10.221'))
        self.assertFalse(network_tester.is_address_in_network('192.168.10.15'))
        self.assertFalse(network_tester.is_address_in_network('172.16.150.220'))

        self.assertRaises(ValueError, Network, '192.168.1.0/0')
        # 0.0.0.0/0 is valid

        self.assertRaises(ValueError, Network, '192.168.1.0/1')
        # 128.0.0.0/1 is valid

        self.assertRaises(ValueError, Network, '192.168.256.255/32')
        self.assertRaises(ValueError, Network, '192.168.255.0/33')
        self.assertRaises(ValueError, Network, '192.168.255.255/24')

    """
    Test for edit value in yaml configuration, reads rules, change value of rule, writes and verifies new value.
    """
    def test_external_config(self):
        external_cfg = Configuration(UnitTest.__test_file)
        external_cfg.read_rules()
        self.assertTrue(external_cfg.is_valid())
        self.assertEqual(external_cfg.path, UnitTest.__test_file, ("Invalid path: " + external_cfg.path))
        external_cfg.read_rules()
        item = "foo"
        backup_value = external_cfg.get_value(item)
        external_cfg.set_rules()
        external_cfg.read_rules()
        new_value = external_cfg.get_value(item)
        self.assertEqual(new_value, backup_value, ("Invalid new value: " + new_value))

    """
    Test for generating port from port range, check for invalid ranges.
    """
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

    """
    Test for using static string in editor mode, finds rule in ansible directory, 
    sets new value to rule, write rule and verify new value. 
    """
    def test_file_edit_str_item(self):
        args = ('-E -k foo -v barbar -d ' + UnitTest.__test_file_dir).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        cfg = None
        test_dir = AnsibleDirectory(params[ArgumentType.AnsibleConfigDir])
        for root, filename in test_dir.iterate_directory_tree():
            cfg = Configuration(os.path.join(root, filename))
            cfg.read_rules()
            self.assertTrue(cfg.is_valid(), "Config file is invalid!")
            cfg.read_rules()
            if cfg.key_exists(params[ArgumentType.ItemKey]):
                cfg.set_value(params[ArgumentType.ItemKey], params[ArgumentType.ItemValue])
                cfg.set_rules()
                break

        self.assertIsNotNone(cfg)
        self.assertTrue(cfg.key_exists(params[ArgumentType.ItemKey]),
                        ("Item " + params[ArgumentType.ItemKey] + " do not exists in " + UnitTest.__test_file + "!"))
        configured_value = cfg.get_value(params[ArgumentType.ItemKey])
        self.assertEqual(configured_value, params[ArgumentType.ItemValue])

    """
    Test for generating IP address from network in editor mode,
    generates IP from valid address, finds rule in ansible directory, write new IP and check new value.
    """
    def test_file_edit_generated_ip(self):
        args = ('-E -k ip -n 192.168.100.0/25 -d ' + UnitTest.__test_file_dir).split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)

        ip = Network(params[ArgumentType.Network]).get_random_value()

        cfg = None
        test_dir = AnsibleDirectory(params[ArgumentType.AnsibleConfigDir])
        for root, filename in test_dir.iterate_directory_tree():
            cfg = Configuration(os.path.join(root, filename))
            cfg.read_rules()
            if cfg.key_exists(params[ArgumentType.ItemKey]):
                cfg.set_value(params[ArgumentType.ItemKey], ip)
                cfg.set_rules()
                cfg.write_rules(UnitTest.__test_file)
                break

        self.assertIsNotNone(cfg)
        cfg.read_rules()
        self.assertEqual(ip, cfg.get_value(params[ArgumentType.ItemKey]))

    """
       Test for ansible directory, opens valid directory and count files.
    """
    def test_ansible_dir_count(self):
        args = ('-E -d ' + os.path.join(UnitTest.__root_folder, 'include', 'template', 'lamp_simple_centos8') +
                ' -k foo -v barbar').split()
        arg_parser = ArgParser()
        params = arg_parser.parse(args)
        ans_dir = AnsibleDirectory(params[ArgumentType.AnsibleConfigDir])
        if __debug__:
            for path, filename in ans_dir.iterate_directory_tree():
                print(os.path.join(path, filename))
        else:
            for _ in ans_dir.iterate_directory_tree():
                pass
        result: int = ans_dir.count_files_in_tree()
        self.assertEqual(result, 17, ('Invalid files number: ' + str(result)))

    """
    Test for deriving child classes used for dynamic values.
    """
    def test_dynamic_types_interface(self):
        self.assertTrue(issubclass(PortRange, DynamicValue))
        self.assertTrue(issubclass(Network, DynamicValue))
        self.assertTrue(issubclass(ListFileReader, DynamicValue))

    """
    Test of type detector for detection all dynamic types: Network, Port range and text file.
    """
    def test_type_detection(self):
        detector = DynamicTypeDetector()

        valid_net: str = '192.168.10.0/24'
        self.assertTrue(detector.is_network(valid_net))
        self.assertEqual(detector.detect_type(valid_net), ArgumentType.Network)

        valid_port: str = '1011-1012'
        self.assertTrue(detector.is_port_range(valid_port))
        self.assertEqual(detector.detect_type(valid_port), ArgumentType.PortRange)

        invalid_port: str = '80'
        with self.assertRaises(InvalidPortRangeException):
            _ = detector.detect_type(invalid_port)

        invalid_network: str = '192.156.156.256/33'
        with self.assertRaises(InvalidPortRangeException):
            _ = detector.detect_type(invalid_network)

    """
        Test for text file with one record per line, reads valid file and check all values.
    """
    def test_simple_text_detection_read(self):
        detector = DynamicTypeDetector()
        valid_file: str = os.path.join(UnitTest.__root_folder, 'include', 'test', 'source', 'passwords.txt')
        self.assertEqual(detector.detect_type(valid_file), ArgumentType.RandomPickFile)

        reader = ListFileReader(valid_file)
        self.assertEqual(reader.reader.get_item_count(), 7)
        self.assertEqual(reader.reader.read_value(6), 'heslopass')
        self.assertTrue(reader.get_random_value() in {'heslo', 'heslo1', 'heslo2', 'password',
                                                      'heslo123', 'pass12345', 'heslopass'})

    """
    Test for CSV file, reads valid CSV file and check all values.
    """
    def test_csv_detection_read(self):
        detector = DynamicTypeDetector()
        valid_file: str = os.path.join(UnitTest.__root_folder, 'include', 'test', 'source', 'logins.csv')
        self.assertEqual(detector.detect_type(valid_file), ArgumentType.RandomPickFile)

        reader = ListFileReader(valid_file)
        self.assertEqual(reader.reader.get_item_count(), 6)
        self.assertEqual(reader.reader.read_value(0), 'username')
        self.assertEqual(reader.reader.read_value(2), 'user')
        self.assertEqual(reader.reader.read_value(4), 'visible_login')
        self.assertEqual(reader.reader.read_value(5), 'last_login')
        self.assertTrue(reader.get_random_value() in {'username', 'login', 'user', 'login_name',
                                                      'visible_login', 'last_login'})

    """
    Test for reading generator configuration, read config and check for categories and first rule.
    """
    def test_input_config(self):
        config = Configuration(os.path.join(UnitTest.__root_folder, 'include', 'generator_config.yml'))
        config.read_rules()
        self.assertTrue(config.is_valid())

        config.read_rules()
        self.assertTrue(config.key_exists('general'))
        self.assertTrue(config.key_exists('static'))
        self.assertTrue(config.key_exists('dynamic'))
        self.assertTrue(config.key_exists('iterations'))

    """
    Test valid regex possibilities, including simple math operations,
    such as addition, subtracting, multiplication, dividing and operation modulo.
    """
    def test_iterator_regex(self):
        self.assertTrue(IteratorRegex.is_iterator_regex('<#>'))
        self.assertIs(IteratorRegex('<#>', 0).number, 0)

        self.assertTrue(IteratorRegex.is_iterator_regex('<#+1>'))
        self.assertIs(IteratorRegex('<#+1>', 1).number, 2)

        self.assertTrue(IteratorRegex.is_iterator_regex('<#-1>'))
        self.assertIs(IteratorRegex('<#-1>', 2).number, 1)

        self.assertTrue(IteratorRegex.is_iterator_regex('<#*2>'))
        self.assertIs(IteratorRegex('<#*2>', 2).number, 4)

        self.assertTrue(IteratorRegex.is_iterator_regex('<#/2>'))
        self.assertIs(IteratorRegex('<#/2>', 4).number, 2)

        self.assertTrue(IteratorRegex.is_iterator_regex('<#%2>'))
        self.assertIs(IteratorRegex('<#%2>', 3).number, 1)

    """
    Test invalid regex possibilities   
    """
    def test_iterator_invalid_regex(self):
        self.assertFalse(IteratorRegex.is_iterator_regex('<##>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#++2>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#%x>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#xx>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#+>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#2>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#+123456>'))
        self.assertFalse(IteratorRegex.is_iterator_regex('<#+0.2>'))

    """
    Test for verify vault feature, reads, writes rules to test files and verify write.
    """
    def test_vault(self):
        src_path = os.path.join(UnitTest.__root_folder, 'include', 'enc_generator_config.yml')
        dst_path = os.path.join(UnitTest.__root_folder, 'include', 'enc_generator_config_test.yml')
        shutil.copy2(src_path, dst_path)
        self.assertTrue(is_vault_file(dst_path))

        password = 'password'
        vault = FileVault(filepath=dst_path, password=password)
        content = vault.read_file()
        vault.write_file(content)
        new_content = vault.read_file()
        self.assertTrue(content == new_content)

        os.remove(dst_path)
        self.assertFalse(os.path.isfile(dst_path))


if __name__ == '__main__':
    unittest.main()
