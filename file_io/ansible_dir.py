"""
Class representing object above ansible directory for iterating over files in dictionary, counting files and copy
directory structure with all subdirectories and files.
"""

from .logger import Logger

from datetime import datetime
import os
import os.path
import pathlib
import shutil


class AnsibleDirectory(object):
    def __init__(self, directory_path: str):
        if os.path.isdir(directory_path):
            self.__path = directory_path
        elif os.path.isfile(directory_path):
            raise FileExistsError
        else:
            raise IOError

    def iterate_directory_tree(self) -> str:
        for root, subdir, files in os.walk(self.__path):
            for filename in files:
                yield root, filename

    def iterate_directory_tree_with_open(self, action, open_mode: str = 'r'):
        for root, subdir, files in os.walk(self.__path):
            for filename in files:
                with open(os.path.join(root, filename), open_mode) as config_file:
                    action(config_file)

    def count_files_in_tree(self) -> int:
        counter: int = 0
        for _ in self.iterate_directory_tree():
            counter += 1
        return counter

    @staticmethod
    def copy_directory(src: str, dst: str, symlinks=False, ignore=None):
        if os.path.isdir(src):
            if not os.path.isdir(dst):
                pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        else:
            Logger.write_error_log("src: " + src + ", dst:" + dst)
            raise FileNotFoundError

    @staticmethod
    def create_dst_directory(dst: str) -> str:
        if not os.path.isdir(dst):
            try:
                pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
            except Exception:
                raise
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%m-%Y_%H:%M:%S")
        dst_folder = os.path.join(dst, timestampStr)
        os.mkdir(dst_folder)
        return dst_folder
