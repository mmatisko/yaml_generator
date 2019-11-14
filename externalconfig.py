from yamlio import YamlIo


class ExternalConfig(object):
    def __init__(self, path: str):
        self.yml_object = object()
        try:
            self.yml_object = YamlIo(path)
        except FileNotFoundError:
            print("Invalid external config path arrived!")

    def verify(self) -> bool:
        return self.yml_object.is_valid(self.yml_object.get_path())

    def get_rules(self) -> dict:
        self.yml_object.read()
        rules = self.yml_object.get_rules()
        return rules

    def get_path(self) -> str:
        return self.yml_object.get_path()

    # just for testing, will be deleted
    def get_yaml_object(self) -> YamlIo:
        return self.yml_object
