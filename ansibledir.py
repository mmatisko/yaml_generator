from configuration import Configuration
import io
import os.path


class AnsibleDirectory(object):
    def __init__(self, directory_path: str):
        if os.path.isdir(directory_path):
            self.path = directory_path
        else:
            raise FileExistsError

    def iterate_directory_tree(self, action, open_mode: str = 'r'):
        for root, subdir, files in os.walk(self.path):
            for filename in files:
                with open(os.path.join(root, filename), open_mode) as config_file:
                    action(config_file)

    def count_files_in_tree(self) -> int:
        counter: int = 0
        for _, _, _ in os.walk(self.path):
            counter += 1
        return counter
