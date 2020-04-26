"""
Class for pre-processing inputs with valid regex, evaluates regex in input value and replace with
result of evaluated math operation and iteration number represented by #.
"""


import re


class IteratorRegex:
    __regex = re.compile("<#([+\-*/%](\d{1,5}))?>")

    def __init__(self, input_value: str, iteration: int):
        self.__input_value = input_value
        self.__iteration = iteration
        self.__regex_part: str = IteratorRegex.__find_regex_in_str(input_value).group(0)
        self.__number: int = self.__parse()
        self.__output_value = input_value.replace(self.__regex_part, str(self.__number))

    def __parse(self) -> int:
        regex_str = self.__regex_part.strip('<>')
        regex_str = regex_str.replace('#', str(self.__iteration))
        return int(eval(regex_str))

    @property
    def number(self) -> int:
        return self.__number

    @property
    def value(self) -> str:
        return self.__output_value

    @staticmethod
    def __find_regex_in_str(input_str: str):
        return IteratorRegex.__regex.search(input_str)

    @staticmethod
    def is_iterator_regex(input_str: str) -> bool:
        return bool(IteratorRegex.__find_regex_in_str(input_str))
