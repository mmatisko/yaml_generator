import io
import os.path
import yaml
import yaml.parser
import yaml.scanner


class YamlIo(object):
    def __init__(self, path: str):
        self.path: str = path
        self.rules: dict = {}
        if os.path.isfile(self.path) and self.read():
            pass
        else:
            raise NotValidYamlFileError

    def is_valid(self) -> bool:
        return (isinstance(self.rules, dict) or isinstance(self.rules, list)) and len(self.rules) > 0
    
    def read(self) -> bool:
        try:
            with io.open(self.path, 'r') as in_file:
                self.rules = yaml.safe_load(in_file)
                return len(self.rules) > 0
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            pass

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


class NotValidYamlFileError(Exception):
    @staticmethod
    def what():
        return "Not valid YAML file!"
