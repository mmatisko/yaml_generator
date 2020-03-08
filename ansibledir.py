from logger import Logger

import os
import os.path
import shutil


class AnsibleDirectory(object):
    def __init__(self, directory_path: str):
        if os.path.isdir(directory_path):
            self.path = directory_path
        else:
            raise FileExistsError

    def iterate_directory_tree(self) -> str:
        for root, subdir, files in os.walk(self.path):
            for filename in files:
                yield root, filename

    def iterate_directory_tree_with_open(self, action, open_mode: str = 'r'):
        for root, subdir, files in os.walk(self.path):
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
                os.mkdir(dst)
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        else:
            print(Logger.get_error_log("src: " + src + ", dst:" + dst))
            raise FileNotFoundError
