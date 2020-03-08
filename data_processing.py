from ansibledir import AnsibleDirectory
from argparser import AppMode, ArgumentType
from configuration import Configuration
from list_reader import ListFileReader
from logger import Logger
from network import Network
from portrange import PortRange
from type_detector import DynamicTypeDetector

import os.path


class DataProcessing(object):
    arg_type_to_obj_dict: dict = {ArgumentType.Network: Network,
                                  ArgumentType.PortRange: PortRange,
                                  ArgumentType.RandomPickFile: ListFileReader}

    def __init__(self, params: dict):
        self.params: dict = params

    def process(self):
        if self.params[ArgumentType.AppMode] is AppMode.Edit:
            self.edit_mode_process()
        else:
            self.generate_mode_process()

    def __get_new_value(self) -> str:
        # dynamic argument value
        for key, value in DataProcessing.arg_type_to_obj_dict.items():
            if key in self.params.keys():
                return DataProcessing.__get_new_value_for_type(arg_type=key, key=self.params[key])

        # static argument value
        if ArgumentType.ItemValue in self.params.keys():
            return self.params[ArgumentType.ItemValue]
        else:
            raise ValueError("No new value provided!")

    @staticmethod
    def __get_new_value_for_type(arg_type: ArgumentType, key: str):
        if arg_type in {ArgumentType.Network, ArgumentType.PortRange, ArgumentType.RandomPickFile}:
            try:
                value = DataProcessing.arg_type_to_obj_dict[arg_type]
                helper_obj = value(key)
                if helper_obj.is_valid:
                    return helper_obj.get_random_value()
            except ValueError:
                Logger.get_error_log("Generating value error!")
        else:
            raise ValueError("Unsupported argument type provided!")

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

        input_dir = self.params[ArgumentType.AnsibleConfigDir] if ArgumentType.AnsibleConfigDir in self.params.keys() \
            else gen_conf.get_value('input')
        output_dir = self.params[ArgumentType.OutputFolder] if ArgumentType.OutputFolder in self.params.keys() \
            else gen_conf.get_value('output')
        output_dir_with_timestamp = AnsibleDirectory.create_dst_directory(dst=output_dir)

        for index in range(iterations):
            output_dir_full_path = os.path.join(output_dir_with_timestamp, str(index))
            AnsibleDirectory.copy_directory(src=input_dir, dst=output_dir_full_path)
            ans_dir = AnsibleDirectory(directory_path=output_dir_full_path)

            for key, value in gen_conf.get_value('static')[0].items():
                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    DataProcessing.set_value_in_file(key=key, value=value, config_path=full_filepath)

            for key, value in gen_conf.get_value('dynamic')[0].items():
                value_type = detector.detect_type(value)
                new_value = DataProcessing.__get_new_value_for_type(arg_type=value_type, key=value)

                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    DataProcessing.set_value_in_file(key=key, value=new_value, config_path=full_filepath)
