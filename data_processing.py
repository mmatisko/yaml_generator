from ansibledir import AnsibleDirectory
from argparser import AppMode, ArgumentType
from configuration import Configuration
from generator_rule import GeneratorRule, GeneratorRuleType

import os.path


class DataProcessing(object):
    def __init__(self, params: dict):
        self.params: dict = params

    def process(self):
        if self.params[ArgumentType.AppMode] is AppMode.Edit:
            self.__edit_mode_process()
        else:
            self.__generate_mode_process()

    @staticmethod
    def __get_dynamic_rule_key(params: dict) -> ArgumentType:
        if ArgumentType.Network in params:
            return ArgumentType.Network
        elif ArgumentType.PortRange in params:
            return ArgumentType.PortRange
        elif ArgumentType.RandomPickFile in params:
            return ArgumentType.RandomPickFile
        else:
            return None

    @staticmethod
    def __set_value_in_file(key: str, value: str, config_path: str) -> bool:
        config = Configuration(config_path)
        if config.is_valid():
            config.read_rules()
            if config.key_exists(key):
                config.set_value(that_key=key, new_value=value)
                config.write_rules(config_path)
                return True
        return False

    def __edit_mode_process(self):
        ans_dir = AnsibleDirectory(directory_path=self.params[ArgumentType.AnsibleConfigDir])
        for root, filename in ans_dir.iterate_directory_tree():
            full_filepath = os.path.join(root, filename)

            new_value_type = self.__get_dynamic_rule_key(self.params)

            new_value = self.params[new_value_type] if new_value_type is not None \
                else self.params[ArgumentType.ItemValue]

            arg_type = GeneratorRuleType.Dynamic if new_value_type is not None else GeneratorRuleType.Static
            new_value = new_value if new_value is not None else self.params[ArgumentType.ItemValue]
            gen_rule = GeneratorRule(name=self.params[ArgumentType.ItemKey], value=new_value, rule_type=arg_type)

            if DataProcessing.__set_value_in_file(key=self.params[ArgumentType.ItemKey],
                                                  value=gen_rule.get_value(0),
                                                  config_path=full_filepath):
                return

    def __generate_mode_process(self):
        gen_conf = Configuration(self.params[ArgumentType.ConfigFile])
        gen_conf.read_rules()
        iterations = gen_conf.get_value('iterations')
        jinja_files = set()

        input_dir = self.params[ArgumentType.AnsibleConfigDir] if ArgumentType.AnsibleConfigDir in self.params.keys() \
            else gen_conf.get_value('input')
        output_dir = self.params[ArgumentType.OutputFolder] if ArgumentType.OutputFolder in self.params.keys() \
            else gen_conf.get_value('output')
        output_dir_with_timestamp = AnsibleDirectory.create_dst_directory(dst=output_dir)

        rules: list = []
        for key, value in gen_conf.get_value('static')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Static))
        for key, value in gen_conf.get_value('dynamic')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Dynamic))

        for iteration_index in range(iterations):
            output_dir_full_path = os.path.join(output_dir_with_timestamp, str(iteration_index))
            AnsibleDirectory.copy_directory(src=input_dir, dst=output_dir_full_path)
            ans_dir = AnsibleDirectory(directory_path=output_dir_full_path)

            if len(jinja_files) is 0:
                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    for rule in rules:
                        if (DataProcessing.__set_value_in_file(key=rule.name,
                                                               value=rule.get_value(iteration_index),
                                                               config_path=full_filepath)):
                            jinja_files.add(full_filepath)
            else:
                for full_jinja_path in jinja_files:
                    for rule in rules:
                        DataProcessing.__set_value_in_file(key=rule.name,
                                                           value=rule.get_value(iteration_index),
                                                           config_path=full_jinja_path)
