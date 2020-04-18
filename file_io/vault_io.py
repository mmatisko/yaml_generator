from ansible_vault import Vault


class FileVault(object):
    def __init__(self, filepath: str, password: str):
        self.__filepath: str = filepath
        self.__password: str = password
        self.__vault: Vault = Vault(self.__password)

    def read_file(self) -> str:
        if self.__password is '':
            raise ValueError
        with open(self.__filepath, 'r') as stream:
            return self.__vault.load(stream.read())

    def write_file(self, rules, path: str = ''):
        if path == '':
            path = self.__filepath
        with open(path, 'w') as stream:
            self.__vault.dump(rules, stream)

    @property
    def password(self) -> str:
        return self.__password


def is_vault_file(filepath: str) -> bool:
    with open(filepath, 'r') as file:
        first_line = file.readline()
        return first_line.startswith("$ANSIBLE_VAULT;1.1")
