import re


class IteratorRegex:
    regex = re.compile("<#([+\-*/%](\d{1,5}))?>")

    def __init__(self, input_value: str, iteration: int):
        self.input_value = input_value
        self.iteration = iteration
        self.regex_part: str = IteratorRegex.__find_regex_in_str(input_value).group(0)
        self.number: int = self.__parse()
        self.output_value = input_value.replace(self.regex_part, str(self.number))

    def __parse(self) -> int:
        regex_str = self.regex_part.strip('<>')
        regex_str = regex_str.replace('#', str(self.iteration))
        return int(eval(regex_str))

    @property
    def value(self) -> str:
        return self.output_value

    @staticmethod
    def __find_regex_in_str(input_str: str):
        return IteratorRegex.regex.search(input_str)

    @staticmethod
    def is_iterator_regex(input_str: str) -> bool:
        return bool(IteratorRegex.__find_regex_in_str(input_str))
