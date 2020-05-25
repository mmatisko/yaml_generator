"""
Class representing IO operations above plain text yaml file, using VaultIO if encrypted yaml file using ansible vault.
"""

from .vault_io import FileVault, is_vault_file

import io
import os.path
import yaml
from yaml import parser, scanner


class YamlIo(object):
    def __init__(self, path: str, password: str = None):
        self.__path: str = path
        self.__rules: dict = {}
        self.__encrypted: bool = False
        self.__vault: FileVault = None
        self.__vault_pass: str = password
        if not os.path.isfile(self.__path):
            raise IOError

    def is_valid(self) -> bool:
        return (isinstance(self.__rules, dict) or isinstance(self.__rules, list)) and len(self.__rules) > 0
    
    def read(self) -> bool:
        try:
            if is_vault_file(self.__path):
                self.__encrypted = True
                self.__vault = FileVault(filepath=self.__path, password=self.__vault_pass)
                self.__rules = self.__vault.read_file()
            else:
                with io.open(self.__path, 'r') as in_file:
                    self.__rules = yaml.safe_load(in_file)
            return len(self.__rules) > 0
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            return False

    def write(self, path=''):
        if path == '':
            path = self.__path
        if self.__encrypted:
            self.__vault.write_file(rules=self.__rules)
        else:
            with io.open(path, 'w', encoding='utf-8') as out_file:
                yaml.safe_dump(self.__rules, out_file, default_flow_style=False, allow_unicode=True)

    def encrypt_on_write(self):
        if not self.__encrypted:
            self.__encrypted = True
            self.__vault = FileVault(filepath=self.__path, password=self.__vault_pass)

    def set_rules(self, rules: dict):
        self.__rules = rules

    @property
    def rules(self) -> dict:
        return self.__rules

    @property
    def path(self) -> str:
        return self.__path

    @property
    def password(self) -> str:
        return self.__vault_pass
