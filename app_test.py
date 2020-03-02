from ansibledir import AnsibleDirectory
from configuration import Configuration
import main

import unittest
import os
import shutil


class AppTest(unittest.TestCase):
    generator_config: str = './include/generator_config.yml'
    template_directory: str = './include/lamp_simple_centos8/'
    testing_directory: str = './testing/lamp_simple_centos8/'
    output_directory: str = './testing_output/'
    iteration_count: int = 3

    def setUp(self) -> None:
        AppTest.__clean_testing_folder(AppTest.testing_directory)
        AppTest.__clean_testing_folder(AppTest.output_directory)
        AppTest.__prepare_testing_folder(src=AppTest.template_directory, dst=AppTest.testing_directory)

    def tearDown(self) -> None:
        AppTest.__clean_testing_folder(AppTest.testing_directory)
        AppTest.__clean_testing_folder(AppTest.output_directory)

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
        self.assertTrue(AppTest.__compare_testing_folders(AppTest.template_directory, AppTest.testing_directory))

    def test_app_edit_mode(self):
        args: list = ('-E -d ' + AppTest.testing_directory + ' -k ntpserver -n 192.168.1.4/30').split()
        # args: list = ('-E -d ' + AppTest.testing_directory + ' -k httpd_port -p 81-90').split()
        # args: list = ('-E -d ' + AppTest.testing_directory + ' -k httpd_port -p 81-90').split()
        # args: list = ('-E -d ' + AppTest.testing_directory + ' -k repository
        # -v http://github.com/bennojoy/mywebapp.git').split()
        main.main(args)

        self.assertTrue(os.path.isdir(AppTest.testing_directory))

        test_conf = Configuration('./testing/lamp_simple_centos8/group_vars/all')
        test_conf.read_rules()
        new_value = test_conf.get_value('ntpserver')
        valid_values = {'192.168.1.5', '192.168.1.6'}
        self.assertTrue(new_value in valid_values)

    def test_app_generate_mode(self):
        args: list = ('-G -c ' + AppTest.generator_config + ' -d ' + AppTest.testing_directory).split()
        main.main(args)

        self.assertTrue(os.path.isdir(AppTest.output_directory))
        for index in range(AppTest.iteration_count):
            self.assertTrue(AppTest.__compare_testing_folders(AppTest.template_directory,
                                                              os.path.join(AppTest.output_directory, str(index))))
