from ansibledir import AnsibleDirectory
from configuration import Configuration
import main

import unittest
import os
import shutil


class AppTest(unittest.TestCase):
    __generator_config: str = './include/generator_config.yml'
    __template_directory: str = './include/template/lamp_simple_centos8/'
    __testing_directory: str = './app_test/input/lamp_simple_centos8/'
    __output_directory: str = './app_test/output/'
    __iteration_count: int = 3

    def setUp(self) -> None:
        AppTest.__clean_testing_folder(AppTest.__testing_directory)
        AppTest.__clean_testing_folder(AppTest.__output_directory)
        AppTest.__prepare_testing_folder(src=AppTest.__template_directory, dst=AppTest.__testing_directory)

    def tearDown(self) -> None:
        AppTest.__clean_testing_folder(AppTest.__testing_directory[:10])
        AppTest.__clean_testing_folder(AppTest.__output_directory)

    @staticmethod
    def __clean_testing_folder(path):
        if os.path.isdir(path):
            shutil.rmtree(path)

    @staticmethod
    def __prepare_testing_folder(src, dst, symlinks=False, ignore=None):
        AnsibleDirectory.copy_directory(src=src, dst=dst, symlinks=symlinks, ignore=ignore)

    @staticmethod
    def __compare_testing_folders(src, dst) -> bool:
        for root, subdir, files in os.walk(src):
            actual_subfolder = root[len(src):]
            for filename in files:
                if not os.path.isfile(os.path.join(dst, actual_subfolder, filename)):
                    return False
        return True

    def test_testing_folder_methods(self):
        self.assertTrue(AppTest.__compare_testing_folders(AppTest.__template_directory, AppTest.__testing_directory))

    def test_app_edit_mode(self):
        args: list = {('ntpserver', '-n 192.168.1.4/30', ('192.168.1.5', '192.168.1.6')),
                      ('httpd_port', '-p 81-85', (81, 82, 83, 84, 85)),
                      ('repository', '-v http://github.com/bennojoy/mywebapp.git',
                      ('http://github.com/bennojoy/mywebapp.git',))}

        for key, value, expected_values in args:
            program_args = ('-E -d ' + AppTest.__testing_directory + ' -k ' + key + ' ' + value).split()
            main.main(program_args)

            self.assertTrue(os.path.isdir(AppTest.__testing_directory))
            test_conf = Configuration(AppTest.__testing_directory + '/group_vars/all')
            test_conf.read_rules()
            new_value = test_conf.get_value(key)
            self.assertTrue(new_value in expected_values)

    def test_app_generate_mode(self):
        args: list = ('-G -c ' + AppTest.__generator_config + ' -d ' + AppTest.__testing_directory).split()
        main.main(args)

        self.assertTrue(os.path.isdir(AppTest.__output_directory))

    def test_invalid_params(self):
        args_mode_only: list = '-G'.split()
        args_no_config: list = ('-G -d' + AppTest.__testing_directory).split()

        self.assertRaises(ValueError, main.main, args_no_config)
        self.assertRaises(ValueError, main.main, args_mode_only)

        args_mode_only: list = '-E'.split()
        args_no_key: list = '-E -v value'.split()
        args_no_value: list = '-E -k key -d dir'.split()
        args_duplicate_item: list = '-E -k key -k key -v value'.split()
        args_multiple_values: list = '-E -k key -v value -f pass_file.txt'.split()

        self.assertRaises(ValueError, main.main, args_mode_only)
        self.assertRaises(ValueError, main.main, args_no_key)
        self.assertRaises(ValueError, main.main, args_no_value)
        self.assertRaises(ValueError, main.main, args_duplicate_item)
        self.assertRaises(ValueError, main.main, args_multiple_values)


if __name__ == "__main__":
    tester = AppTest()
    tester.test_app_edit_mode()
    tester.test_app_generate_mode()
