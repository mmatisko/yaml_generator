import os.path


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
