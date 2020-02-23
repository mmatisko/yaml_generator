from yamlio import NotValidYamlFileError, YamlIo
from logger import Logger


class Configuration(object):
    def __init__(self, path: str):
        self.yml_object = None
        self.rules: dict = {}
        try:
            self.yml_object = YamlIo(path)
        except NotValidYamlFileError:
            Logger().get_debug_log("Not yaml file: " + path)
            # print("Invalid external config path arrived!")
        except IOError:
            print("Unknown IO error")

    def is_valid(self) -> bool:
        return self.yml_object is not None and self.yml_object.is_valid()

    def read_rules(self):
        self.yml_object.read()
        self.rules = self.yml_object.get_rules()

    def set_value(self, that_key: str, new_value: str):
        self.__iterate_dict_for_set(self.rules, that_key, new_value)

    def get_value(self, that_key: str):
        return self.__iterate_rules_for_get(that_key, return_value=True)

    def key_exists(self, that_key: str):
        return self.__iterate_rules_for_get(that_key, return_value=False)

    def __iterate_rules_for_get(self, that_key: str, return_value: bool):
        if isinstance(self.rules, list):
            result = Configuration.__iterate_list_for_get(working_list=self.rules, that_key=that_key)
        elif isinstance(self.rules, dict):
            result = Configuration.__iterate_dict_for_get(self.rules, that_key)
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
            check_result = Configuration.__get_iteration_subroutine(value, that_key)
            if check_result is not None:
                return check_result

        return

    @staticmethod
    def __iterate_list_for_get(working_list: list, that_key: str):
        for key in working_list:
            if key == that_key:
                return key
            check_result = Configuration.__get_iteration_subroutine(key, that_key)
            if check_result is not None:
                return check_result

    @staticmethod
    def __get_iteration_subroutine(item, that_key: str):
        if isinstance(item, list):
            result = Configuration.__iterate_list_for_get(item, that_key)
            if result is not None:
                return result
        elif isinstance(item, dict):
            result = Configuration.__iterate_dict_for_get(item, that_key)
            if result is not None:
                return result
        else:
            return None

    @staticmethod
    def __iterate_dict_for_set(working_dict: dict, that_key: str, new_value: str):
        for key, value in working_dict.items():
            if isinstance(value, dict):
                Configuration.__iterate_dict_for_set(value, that_key, new_value)
            else:
                if key == that_key:
                    working_dict[key] = new_value
                    return

    def set_rules(self):
        self.yml_object.set_rules(self.rules)

    def write_rules(self, path=''):
        self.yml_object.write(path)

    def get_path(self) -> str:
        return self.yml_object.get_path()
