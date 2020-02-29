from ansibledir import AnsibleDirectory
from argparser import AppMode, ArgumentType
from configuration import Configuration
from list_reader import ListFileReader
from network import Network
from portrange import PortRange
from type_detector import DynamicTypeDetector

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
                except ValueError:
                    print("Generating new value error!")

        if ArgumentType.ItemValue in self.params.keys():
            return self.params[ArgumentType.ItemValue]
        else:
            raise ValueError("No new value provided!")

    @staticmethod
    def set_value_in_file(key: str, value: str, config_path: str) -> bool:
        config = Configuration(config_path)
        if config.is_valid():
            config.read_rules()
            if config.key_exists(key):
                config.set_value(that_key=key, new_value=value)
                config.write_rules(config_path)
                return True
        return False

    def edit_mode_process(self):
        ans_dir = AnsibleDirectory(directory_path=self.params[ArgumentType.AnsibleConfigDir])
        for root, filename in ans_dir.iterate_directory_tree():
            full_filepath = os.path.join(root, filename)

            if DataProcessing.set_value_in_file(key=self.params[ArgumentType.ItemKey], value=self.__get_new_value(),
                                                config_path=full_filepath):
                return

    def generate_mode_process(self):
        gen_conf = Configuration(self.params[ArgumentType.ConfigFile])
        gen_conf.read_rules()
        iterations = gen_conf.get_value('iterations')
        detector = DynamicTypeDetector()
        for index in range(iterations):
            input_dir = self.params[ArgumentType.AnsibleConfigDir] if ArgumentType.AnsibleConfigDir \
                in self.params.keys() else gen_conf.get_value('input')
            output_dir = self.params[ArgumentType.OutputFolder] if ArgumentType.OutputFolder in self.params.keys() \
                else gen_conf.get_value('input')
            output_dir = os.path.join(output_dir, str(index))
            AnsibleDirectory.copy_directory(src=input_dir, dst=output_dir)
            ans_dir = AnsibleDirectory(directory_path=self.params[ArgumentType.AnsibleConfigDir])

            for key, value in gen_conf.get_value('static')[0].items():
                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    DataProcessing.set_value_in_file(key=key, value=value, config_path=full_filepath)

            for key, value in gen_conf.get_value('dynamic')[0].items():
                value_type = detector.detect_type(value)

                # TODO: add value generation

                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    DataProcessing.set_value_in_file(key=key, value=value, config_path=full_filepath)
