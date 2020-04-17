from ansibledir import AnsibleDirectory
from argparser import AppMode, ArgumentType
from configuration import Configuration
from generator_rule import GeneratorRule, GeneratorRuleType
from vault import is_vault_file

from getpass import getpass
import os.path


class DataProcessing(object):
    def __init__(self, params: dict):
        self.params: dict = params
        self.ansible_cfg_pass: str = ''
        self.generator_cfg_pass: str = ''

    def process(self):
        self.ansible_cfg_pass = getpass('Enter Ansible Vault password for Ansible configuration (confirm empty\n'
                                        'for plain text output using plain text template:')
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

    def __set_value_in_file(self, key: str, value: str, config_path: str) -> bool:
        config = Configuration(path=config_path, password=self.ansible_cfg_pass)
        config.read_rules()
        if config.is_valid():
            config.read_rules()
            if config.key_exists(key):
                config.set_value(that_key=key, new_value=value)
                config.write_rules(config_path)
                return True
        return False

    def __edit_mode_process(self):
        ans_dir = AnsibleDirectory(directory_path=self.params[ArgumentType.AnsibleConfigDir])

        new_value_type = self.__get_dynamic_rule_key(self.params)
        new_value = self.params[new_value_type] if new_value_type is not None \
            else self.params[ArgumentType.ItemValue]

        arg_type = GeneratorRuleType.Dynamic if new_value_type is not None else GeneratorRuleType.Static
        new_value = new_value if new_value is not None else self.params[ArgumentType.ItemValue]
        gen_rule = GeneratorRule(name=self.params[ArgumentType.ItemKey], value=new_value, rule_type=arg_type)

        for root, filename in ans_dir.iterate_directory_tree():
            full_filepath = os.path.join(root, filename)

            if self.__set_value_in_file(key=self.params[ArgumentType.ItemKey],
                                        value=gen_rule.get_value(0),
                                        config_path=full_filepath):
                return

    def __generate_mode_process(self):
        if is_vault_file(self.params[ArgumentType.ConfigFile]):
            self.generator_cfg_pass = getpass('Enter Ansible Vault password for generator configuration (confirm empty'
                                              '\nfor plain text output using plain text template:')
        gen_conf = Configuration(path=self.params[ArgumentType.ConfigFile], password=self.generator_cfg_pass)
        gen_conf.read_rules()
        iterations = gen_conf.get_value('iterations')
        jinja_files = set()

        input_dir = self.params[ArgumentType.AnsibleConfigDir] if ArgumentType.AnsibleConfigDir in self.params.keys() \
            else gen_conf.get_value('input')
        output_dir = self.params[ArgumentType.OutputFolder] if ArgumentType.OutputFolder in self.params.keys() \
            else gen_conf.get_value('output')
        output_dir_with_timestamp = AnsibleDirectory.create_dst_directory(dst=output_dir)
        if input_dir is '' or output_dir is '':
            raise ValueError('Input or output folder not defined!')

        rules: list = []
        for key, value in gen_conf.get_value('static')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Static))
        for key, value in gen_conf.get_value('dynamic')[0].items():
            rules.append(GeneratorRule(name=key, value=value, rule_type=GeneratorRuleType.Dynamic))

        for iteration_index in range(iterations):
            rules_left = rules.copy()
            output_dir_full_path = os.path.join(output_dir_with_timestamp, str(iteration_index))
            AnsibleDirectory.copy_directory(src=input_dir, dst=output_dir_full_path)
            ans_dir = AnsibleDirectory(directory_path=output_dir_full_path)

            if len(jinja_files) is 0:
                for root, filename in ans_dir.iterate_directory_tree():
                    full_filepath = os.path.join(root, filename)
                    for rule in rules:
                        if rule in rules_left:
                            if (self.__set_value_in_file(key=rule.name,
                                                         value=rule.get_value(iteration_index),
                                                         config_path=full_filepath)):
                                file_with_folder = full_filepath[full_filepath.rfind('/0/')+2:]
                                jinja_files.add(output_dir_with_timestamp + '/^$^$^' + file_with_folder)
                                rules_left.remove(rule)
            else:
                for full_jinja_path in jinja_files:
                    for rule in rules:
                        if rule in rules_left:
                            iteration_path = full_jinja_path.replace('^$^$^', str(iteration_index))
                            if self.__set_value_in_file(key=rule.name,
                                                        value=rule.get_value(iteration_index),
                                                        config_path=iteration_path):
                                rules_left.remove(rule)
