from ansible_vault import Vault
from getpass import getpass


class FileVault(object):
    def __init__(self, filepath: str):
        self.__filepath = filepath
        self.__vault = Vault(FileVault.__load_password())

    def read_file(self) -> str:
        with open(self.__filepath, 'r') as stream:
            return self.__vault.load(stream.read())

    def write_file(self, rules):
        with open(self.__filepath, 'w') as stream:
            self.__vault.dump(rules, stream)

    @staticmethod
    def is_vault_file(filepath: str) -> bool:
        with open(filepath, 'r') as file:
            first_line = file.readline()
            return first_line.startswith("$ANSIBLE_VAULT;1.1")

    @staticmethod
    def __load_password() -> str:
        return getpass("Enter ansible vault password:\n")
