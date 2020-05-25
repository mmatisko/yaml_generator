"""
Class represents rules from yaml file using underlying object YamlIO and VaultIO (if necessary), which uses for reading
and writing to corresponding file. Allows generator reads and writes rules, search for specific key and set encryption
mode to output file.
"""

from file_io import Logger, YamlIo


class Configuration(object):
    def __init__(self, path: str, password: str = None):
        self.__yml_object: YamlIo = None
        self.__rules: dict = {}
        try:
            self.__yml_object = YamlIo(path=path, password=password)
        except IOError:
            print("Unknown IO error")

    def __eq__(self, other):
        return self.__yml_object.path == other.__yml_object.path

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__yml_object.path)

    def is_valid(self) -> bool:
        return self.__yml_object is not None and self.__yml_object.is_valid()

    def read_rules(self):
        if self.__yml_object.read():
            self.__rules = self.__yml_object.rules
        else:
            Logger().write_debug_log("Not yaml file: " + self.__yml_object.path)

    def set_value(self, that_key: str, new_value: str):
        self.__iterate_rules_for_set(that_key=that_key, new_value=new_value)

    def get_value(self, that_key: str):
        return self.__iterate_rules_for_get(that_key, return_value=True)

    def key_exists(self, that_key: str):
        return self.__iterate_rules_for_get(that_key, return_value=False)

    def __iterate_rules_for_get(self, that_key: str, return_value: bool):
        if isinstance(self.__rules, list):
            result = Configuration.__iterate_list_for_get(working_list=self.__rules, that_key=that_key)
        elif isinstance(self.__rules, dict):
            result = Configuration.__iterate_dict_for_get(working_dict=self.__rules, that_key=that_key)
        else:
            raise ValueError("Not valid rules provided!")

        if return_value:
            return result
        else:
            return result is not None

    @staticmethod
    def __iterate_dict_for_get(working_dict: dict, that_key: str):
        for key, value in working_dict.items():
            if key == that_key:
                return value
            check_result = Configuration.__get_iteration_subroutine(item=value, that_key=that_key)
            if check_result is not None:
                return check_result

        return

    @staticmethod
    def __iterate_list_for_get(working_list: list, that_key: str):
        for key in working_list:
            if key == that_key:
                return key
            check_result = Configuration.__get_iteration_subroutine(item=key, that_key=that_key)
            if check_result is not None:
                return check_result

    @staticmethod
    def __get_iteration_subroutine(item, that_key: str):
        if isinstance(item, list):
            result = Configuration.__iterate_list_for_get(working_list=item, that_key=that_key)
            if result is not None:
                return result
        elif isinstance(item, dict):
            result = Configuration.__iterate_dict_for_get(working_dict=item, that_key=that_key)
            if result is not None:
                return result
        else:
            return None

    def __iterate_rules_for_set(self, that_key: str, new_value: str):
        if isinstance(self.__rules, list):
            Configuration.__iterate_list_for_set(working_list=self.__rules, that_key=that_key, new_value=new_value)
        elif isinstance(self.__rules, dict):
            Configuration.__iterate_dict_for_set(working_dict=self.__rules, that_key=that_key, new_value=new_value)
        else:
            raise ValueError("Not valid rules provided!")

    @staticmethod
    def __iterate_dict_for_set(working_dict: dict, that_key: str, new_value: str):
        for key, value in working_dict.items():
            if key == that_key:
                working_dict[key] = new_value
                return
            else:
                Configuration.__set_iteration_subroutine(item=value, that_key=that_key, new_value=new_value)

    @staticmethod
    def __iterate_list_for_set(working_list: list, that_key: str, new_value: str):
        for index in range(len(working_list)):
            if working_list[index] == that_key:
                working_list[index] = new_value
                return
            else:
                Configuration.__set_iteration_subroutine(item=working_list[index], that_key=that_key,
                                                         new_value=new_value)

    @staticmethod
    def __set_iteration_subroutine(item, that_key: str, new_value: str):
        if isinstance(item, list):
            Configuration.__iterate_list_for_set(working_list=item, that_key=that_key, new_value=new_value)
        elif isinstance(item, dict):
            Configuration.__iterate_dict_for_set(working_dict=item, that_key=that_key, new_value=new_value)

    def set_rules(self):
        self.__yml_object.set_rules(self.__rules)

    def write_rules(self, path=''):
        self.__yml_object.write(path)

    @property
    def path(self) -> str:
        return self.__yml_object.path

    def set_encrypted_write(self):
        self.__yml_object.encrypt_on_write()

    def password(self) -> str:
        return self.__yml_object.password
