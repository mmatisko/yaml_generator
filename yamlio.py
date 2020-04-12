import io
import os.path
import yaml
from yaml import parser, scanner
from vault import FileVault


class YamlIo(object):
    def __init__(self, path: str):
        self.__path: str = path
        self.__rules: dict = {}
        if os.path.isfile(self.__path) and self.read():
            pass
        else:
            raise NotValidYamlFileError

    def is_valid(self) -> bool:
        return (isinstance(self.__rules, dict) or isinstance(self.__rules, list)) and len(self.__rules) > 0
    
    def read(self) -> bool:
        try:
            with io.open(self.__path, 'r') as in_file:
                self.__rules = yaml.safe_load(in_file)
                return len(self.__rules) > 0
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            pass

    def write(self, path='') -> bool:
        if path == '':
            path = self.__path
        with io.open(path, 'w', encoding='utf-8') as out_file:
            yaml.safe_dump(self.__rules, out_file, default_flow_style=False, allow_unicode=True)
            return True

    def get_rules(self) -> dict:
        return self.__rules

    def set_rules(self, rules: dict):
        self.__rules = rules

    def get_path(self) -> str:
        return self.__path


class NotValidYamlFileError(Exception):
    @staticmethod
    def what():
        return "Not valid YAML file!"
