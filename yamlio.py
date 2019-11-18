import io
import os.path
import yaml


class YamlIo(object):
    def __init__(self, path: str):
        self.path: str = ''
        self.rules: dict = {}
        if self.is_valid(path):
            self.path = path
        else:
            raise FileNotFoundError

    @staticmethod
    def is_valid(path) -> bool:
        return (path.endswith(".yml") or path.endswith(".yaml")) and os.path.isfile(path)
    
    def read(self) -> bool:
        with io.open(self.path, 'r') as in_file:
            self.rules = yaml.safe_load(in_file)
            return len(self.rules) > 0

    def write(self, path='') -> bool:
        if path == '':
            path = self.path
        with io.open(path, 'w', encoding='utf-8') as out_file:
            yaml.dump(self.rules, out_file, default_flow_style=False, allow_unicode=True)
            return True

    def get_rules(self) -> dict:
        return self.rules

    def set_rules(self, rules: dict):
        self.rules = rules

    def get_path(self) -> str:
        return self.path
