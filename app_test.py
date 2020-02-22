import main

import unittest
import os
import shutil


class AppTest(unittest.TestCase):
    generator_config: str = './include/generator_config.yml'
    template_directory: str = './include/lamp_simple_centos8/'
    testing_directory: str = './testing/lamp_simple_centos8/'
    output_directory: str = './testing/output/'

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
            shutil.rmtree(path[:len(path) - 20])

    @staticmethod
    def __prepare_testing_folder(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

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
        args: str = '-E -c ' + AppTest.generator_config + ' -d ' + AppTest.testing_directory + '-k ntpserver -n ' \
                                                                                               '192.168.1.0/24 '
        main.main(args)

        self.assertTrue(os.path.isdir(AppTest.output_directory))

    def test_app_generate_mode(self):
        args: str = '-G -c ' + AppTest.generator_config + ' -d ' + AppTest.testing_directory
        main.main(args)

        self.assertTrue(os.path.isdir(AppTest.output_directory))
        for index in range(0, 5):
            self.assertTrue(AppTest.__compare_testing_folders(AppTest.template_directory,
                                                              os.path.join(AppTest.output_directory, str(index))))
