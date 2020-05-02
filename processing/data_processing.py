"""
Main processing file, contains core logic for both editor and generator mode.
"""

from .arg_parser import AppMode, ArgumentType
from .configuration import Configuration
from .threadpool import Threadpool
from file_io import AnsibleDirectory, is_vault_file
from rules import GeneratorRule, GeneratorRuleType

from getpass import getpass
import os.path


class DataProcessing(object):
    def __init__(self, params: dict):
        self.__params: dict = params
        self.__ansible_cfg_pass: str = ''
        self.__generator_cfg_pass: str = ''

    def process(self):
        self.__ansible_cfg_pass = getpass('Enter Ansible Vault password for Ansible configuration (confirm empty\n'
                                          'for plain text output using plain text template:')
        if self.__params[ArgumentType.AppMode] is AppMode.Edit:
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
    def __set_value_in_file(key: str, value: str, config: Configuration) -> bool:
        if config.is_valid():
            if config.key_exists(key):
                config.set_value(that_key=key, new_value=value)
                return True
        return False

    def __edit_mode_process(self):
        ans_dir = AnsibleDirectory(directory_path=self.__params[ArgumentType.AnsibleConfigDir])

        new_value_type = self.__get_dynamic_rule_key(self.__params)
        new_value = self.__params[new_value_type] if new_value_type is not None \
            else self.__params[ArgumentType.ItemValue]

        arg_type = GeneratorRuleType.Dynamic if new_value_type is not None else GeneratorRuleType.Static
        new_value = new_value if new_value is not None else self.__params[ArgumentType.ItemValue]
        gen_rule = GeneratorRule(name=self.__params[ArgumentType.ItemKey], value=new_value, rule_type=arg_type)

        for root, filename in ans_dir.iterate_directory_tree():
            full_filepath = os.path.join(root, filename)

            config = Configuration(path=full_filepath, password=self.__ansible_cfg_pass)
            config.read_rules()
            if self.__set_value_in_file(key=self.__params[ArgumentType.ItemKey],
                                        value=gen_rule.get_value(0),
                                        config=config):
                if self.__ansible_cfg_pass is not '':
                    config.set_encrypted_write()
                config.write_rules()
                return

    def __generate_mode_process(self):
        if is_vault_file(self.__params[ArgumentType.ConfigFile]):
            self.__generator_cfg_pass = getpass('Enter Ansible Vault password for generator configuration (confirm '
                                                'empty \nfor plain text output using plain text template:')
        gen_conf = Configuration(path=self.__params[ArgumentType.ConfigFile], password=self.__generator_cfg_pass)
        gen_conf.read_rules()
        iterations = gen_conf.get_value('iterations')
        sensitive_files = set()
        sensitive_configs = set()

        input_dir = self.__params[ArgumentType.AnsibleConfigDir] if \
            ArgumentType.AnsibleConfigDir in self.__params.keys() else gen_conf.get_value('input')
        output_dir = self.__params[ArgumentType.OutputFolder] if ArgumentType.OutputFolder in self.__params.keys() \
            else gen_conf.get_value('output')
        output_dir_with_timestamp = AnsibleDirectory.create_dst_directory(dst=output_dir)
        if input_dir is '' or output_dir is '':
            raise ValueError('Input or output folder not defined!')

        rules: list = []
        for key, value in gen_conf.get_value('static')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Static))
        for key, value in gen_conf.get_value('dynamic')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Dynamic))

        tp = Threadpool()
        for iteration_index in range(iterations):
            rules_left = rules.copy()
            output_dir_full_path = os.path.join(output_dir_with_timestamp, str(iteration_index))
            AnsibleDirectory.copy_directory(src=input_dir, dst=output_dir_full_path)
            ans_dir = AnsibleDirectory(directory_path=output_dir_full_path)

            if len(sensitive_files) is 0:
                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    config = Configuration(path=full_filepath, password=self.__ansible_cfg_pass)
                    config.read_rules()
                    for rule in rules:
                        if rule in rules_left:
                            if (self.__set_value_in_file(key=rule.name,
                                                         value=rule.get_value(iteration_index),
                                                         config=config)):
                                file_with_dir = full_filepath[full_filepath.rfind(os.path.join('', '0', ''))+2:]
                                sensitive_files.add(os.path.join(output_dir_with_timestamp, '^$^$^', file_with_dir))
                                sensitive_configs.add(config)
                                rules_left.remove(rule)
                for sensitive_config in sensitive_configs:
                    if self.__ansible_cfg_pass is not '':
                        sensitive_config.set_encrypted_write()
                    sensitive_config.write_rules()
                sensitive_configs.clear()

            else:
                # item = lambda ansible_cfg_pass: \
                # DataProcessing.__next_iteration(iteration_index, rules, ansible_cfg_pass, sensitive_files)

                # self.__next_iteration(iteration_index, rules, self.__ansible_cfg_pass, sensitive_files)
                tp.add_work(DataProcessing.__next_iteration, iteration_index, rules, self.__ansible_cfg_pass,
                            sensitive_files)
        tp.start_work()

    @staticmethod
    # def __next_iteration(iteration_index: int, rules: list, ansible_cfg_pass: str, sensitive_files: set):
    def __next_iteration(args):
        iteration_index = args[0]
        rules = args[1]
        ansible_cfg_pass = args[2]
        sensitive_files = args[3]

        rules_left = rules.copy()
        sensitive_configs = set()

        for full_jinja_path in sensitive_files:
            iteration_path = full_jinja_path.replace('^$^$^', str(iteration_index))
            config = Configuration(path=iteration_path, password=ansible_cfg_pass)
            config.read_rules()
            for rule in rules:
                if rule in rules_left:
                    if DataProcessing.__set_value_in_file(key=rule.name,
                                                          value=rule.get_value(iteration_index),
                                                          config=config):
                        sensitive_configs.add(config)
                        rules_left.remove(rule)

        for sensitive_config in sensitive_configs:
            if ansible_cfg_pass is not '':
                sensitive_config.set_encrypted_write()
            sensitive_config.write_rules()
        sensitive_configs.clear()
        return True
