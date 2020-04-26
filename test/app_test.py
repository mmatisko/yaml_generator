"""
App Test for testing whole generator in both methods, testing invalid CLI arguments,
each test runs in sandbox environment.
"""

from io import StringIO
import os
import sys
import shutil
import unittest

from file_io import AnsibleDirectory
from processing import Configuration
from ans_gen import main


class AppTest(unittest.TestCase):
    """ using in debug mode only """
    # os.chdir('..')
    __root_folder: str = os.getcwd()

    __generator_config: str = os.path.join(__root_folder, 'include', 'generator_config.yml')
    __template_directory: str = os.path.join(__root_folder, 'include', 'template', 'lamp_simple_centos8', '')
    __testing_directory: str = os.path.join(__root_folder, 'app_test', 'input', 'lamp_simple_centos8', '')

    __generator_config_enc: str = os.path.join(__root_folder, 'include', 'enc_generator_config.yml')
    __template_directory_enc: str = os.path.join(__root_folder, 'include', 'template', 'enc_lamp_simple_centos8', '')
    __testing_directory_enc: str = os.path.join(__root_folder, 'app_test', 'input', 'enc_lamp_simple_centos8', '')

    __output_directory: str = os.path.join(__root_folder, 'app_test', 'output', '')
    __iteration_count: int = 3

    def setUp(self) -> None:
        AppTest.__clean_testing_folder(AppTest.__testing_directory)
        AppTest.__clean_testing_folder(AppTest.__output_directory)
        AppTest.__prepare_testing_folder(src=AppTest.__template_directory, dst=AppTest.__testing_directory)

        AppTest.__clean_testing_folder(AppTest.__testing_directory_enc)
        AppTest.__prepare_testing_folder(src=AppTest.__template_directory_enc, dst=AppTest.__testing_directory_enc)

    def tearDown(self) -> None:
        AppTest.__clean_testing_folder(os.path.join(AppTest.__root_folder, 'app_test', ''))
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

    """
    Test for sandbox environment, does copy of necessary files to separate testing folder.
    """
    def test_testing_folder_methods(self):
        self.assertTrue(AppTest.__compare_testing_folders(src=AppTest.__template_directory,
                                                          dst=AppTest.__testing_directory))

    """
    Test for editor mode, edit all possible rule types in both plain text and encrypted configuration, 
    writes rules and verify new values.
    """
    def test_app_edit_mode(self):
        args: list = [('ntpserver', '-n 192.168.1.4/30', ('192.168.1.5', '192.168.1.6')),
                      ('httpd_port', '-p 81-85', (81, 82, 83, 84, 85)),
                      ('repository', '-v http://github.com/bennojoy/mywebapp.git',
                      ('http://github.com/bennojoy/mywebapp.git',))]

        for working_dir in {AppTest.__testing_directory,
                            AppTest.__testing_directory_enc}:
            for key, value, expected_values in args:
                program_args = ('-E -d ' + working_dir + ' -k ' + key + ' ' + value).split()

                password = 'password'
                test_conf = Configuration(path=os.path.join(working_dir, 'group_vars', 'all'), password=password)
                test_conf.read_rules()
                old_value = test_conf.get_value(key)

                sys.stdin.close()
                sys.stdin = StringIO(password)
                main(program_args)

                self.assertTrue(os.path.isdir(AppTest.__testing_directory))
                test_conf = Configuration(path=os.path.join(working_dir, 'group_vars', 'all'), password=password)
                test_conf.read_rules()
                new_value = test_conf.get_value(key)
                self.assertFalse(old_value is new_value)
                self.assertTrue(new_value in expected_values)

    """
    Test for generator mode, generate configuration using all possible combinations of generator config 
    and input templates and verify their existence.
    """
    def test_app_generate_mode(self):
        pairs: list = [(AppTest.__generator_config, AppTest.__testing_directory, '\n\n'),
                       (AppTest.__generator_config_enc, AppTest.__testing_directory, '\npassword'),
                       (AppTest.__generator_config, AppTest.__testing_directory_enc, 'password\n\n'),
                       (AppTest.__generator_config_enc, AppTest.__testing_directory_enc,
                        'password\npassword\n')]

        for gen_cfg, working_dir, password in pairs:
            args: list = ('-G -c ' + gen_cfg + ' -d ' + working_dir).split()

            sys.stdin.close()
            sys.stdin = StringIO(password)
            main(args)

            self.assertTrue(os.path.isdir(AppTest.__output_directory))

    """
    Test for invalid CLI arguments, like missing required arguments or invalid count of arguments.
    """
    def test_invalid_params(self):
        args_mode_only: list = '-G'.split()
        args_no_config: list = ('-G -d' + AppTest.__testing_directory).split()

        self.assertRaises(ValueError, main, args_no_config)
        self.assertRaises(ValueError, main, args_mode_only)

        args_mode_only: list = '-E'.split()
        args_no_key: list = '-E -v value'.split()
        args_no_value: list = '-E -k key -d dir'.split()
        args_duplicate_item: list = '-E -k key -k key -v value'.split()
        args_multiple_values: list = '-E -k key -v value -f pass_file.txt'.split()

        self.assertRaises(ValueError, main, args_mode_only)
        self.assertRaises(ValueError, main, args_no_key)
        self.assertRaises(ValueError, main, args_no_value)
        self.assertRaises(ValueError, main, args_duplicate_item)
        self.assertRaises(ValueError, main, args_multiple_values)

    """
    Test for missing required arguments in generator mode.
    """
    def test_empty_input_or_output(self):
        args_no_input: list = '-G -c ' + AppTest.__generator_config + ' -d '
        args_no_output: list = '-G -c ' + AppTest.__generator_config + ' -o '

        self.assertRaises(ValueError, main, args_no_input)
        self.assertRaises(ValueError, main, args_no_output)


if __name__ == "__main__":
    tester = AppTest()
    tester.test_app_edit_mode()
    tester.test_app_generate_mode()
