from ansibledir import AnsibleDirectory
from argparser import AppMode, ArgumentType
from configuration import Configuration
from list_reader import ListFileReader
from network import Network
from portrange import PortRange

import os.path


class DataProcessing(object):
    def __init__(self, params: dict):
        self.params: dict = params

    def process(self):
        if self.params[ArgumentType.AppMode] is AppMode.Edit:
            self.edit_mode_process()
        else:
            self.generate_mode_process()

    def __get_new_value(self) -> str:
        pairs: dict = {ArgumentType.Network: Network,
                       ArgumentType.PortRange: PortRange,
                       ArgumentType.RandomPickFile: ListFileReader}

        for key, value in pairs.items():
            if key in self.params.keys():
                try:
                    helper_obj = value(self.params[key])
                    if helper_obj.is_valid:
                        return helper_obj.get_random_value()
                except ValueError as err:
                    print("Generating new value error!")

        if ArgumentType.ItemValue in self.params.keys():
            return self.params[ArgumentType.ItemValue]
        else:
            raise ValueError("No new value provided!")

    def edit_mode_process(self):
        ans_dir = AnsibleDirectory(directory_path=self.params[ArgumentType.AnsibleConfigDir])
        for root, filename in ans_dir.iterate_directory_tree():
            full_filepath = os.path.join(root, filename)
            ansible_file = Configuration(full_filepath)
            if ansible_file.is_valid():
                ansible_file.read_rules()
                if ansible_file.key_exists(self.params[ArgumentType.ItemKey]):
                    new_value = self.__get_new_value()
                    ansible_file.set_value(that_key=self.params[ArgumentType.ItemKey], new_value=new_value)
                    ansible_file.write_rules(full_filepath)
                    return

    def generate_mode_process(self):
        pass
