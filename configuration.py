from yamlio import YamlIo


class Configuration(object):
    def __init__(self, path: str):
        self.yml_object = object()
        self.rules: dict = {}
        try:
            self.yml_object = YamlIo(path)
        except FileNotFoundError:
            print("Invalid external config path arrived!")
        except IOError:
            print("Unknown IO error")

    def verify(self) -> bool:
        return self.yml_object.is_valid(self.yml_object.get_path())

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
        result = Configuration.__iterate_dict_for_get(self.rules, that_key)
        if return_value:
            return result
        else:
            return len(result) > 0

    @staticmethod
    def __iterate_dict_for_get(working_dict: dict, that_key: str):
        for key, value in working_dict.items():
            if isinstance(value, dict):
                result = Configuration.__iterate_dict_for_get(value, that_key)
                if len(result) > 0:
                    return result
            else:
                if key == that_key:
                    return value
        return

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

    @staticmethod
    def is_valid(path: str):
        return YamlIo.is_valid(path)
