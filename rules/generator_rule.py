from file_io import Logger
from .iterator_regex import IteratorRegex
from .type_detector import DynamicTypeDetector, ListFileReader, Network, PortRange
from processing import ArgumentType

from enum import Enum


class GeneratorRuleType(Enum):
    Static = 1
    Dynamic = 2
    General = 3

    def __str__(self):
        return str(self.name)


class GeneratorRule(object):
    arg_type_to_obj_dict: dict = {ArgumentType.Network: Network,
                                  ArgumentType.PortRange: PortRange,
                                  ArgumentType.RandomPickFile: ListFileReader}

    def __init__(self, name: str, value: str, rule_type: GeneratorRuleType):
        self.__name = name
        self.__value = value
        self.__type = rule_type
        self.__detector = DynamicTypeDetector()

    def __preproccess_string(self, iteration: int) -> str:
        if IteratorRegex.is_iterator_regex(self.__value):
            return IteratorRegex(input_value=self.__value, iteration=iteration).value
        else:
            return self.__value

    @staticmethod
    def __get_new_value_for_type(arg_type: ArgumentType, key: str):
        if arg_type in {ArgumentType.Network, ArgumentType.PortRange, ArgumentType.RandomPickFile}:
            try:
                value = GeneratorRule.arg_type_to_obj_dict[arg_type]
                helper_obj = value(key)
                if helper_obj.is_valid:
                    return helper_obj.get_random_value()
            except ValueError:
                Logger.write_error_log("Generating value error!")
        else:
            raise ValueError("Unsupported argument type provided!")

    def get_value(self, iteration: int):
        preprocessed_value = self.__preproccess_string(iteration=iteration)
        if self.__type in [GeneratorRuleType.Static, GeneratorRuleType.General]:
            return preprocessed_value
        else:
            value_type = self.__detector.detect_type(preprocessed_value)
            return GeneratorRule.__get_new_value_for_type(arg_type=value_type, key=preprocessed_value)

    @property
    def name(self):
        return self.__name
