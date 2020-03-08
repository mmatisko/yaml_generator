import re


class IteratorRegex:
    def __init__(self, regex: str, iteration: int):
        self.regex = regex
        self.iteration = iteration
        self.number: int = self.parse()

    def parse(self) -> int:
        regex_str = self.regex.strip('<>')
        regex_str = regex_str.replace('#', str(self.iteration))
        return int(eval(regex_str))

    @property
    def value(self) -> int:
        return self.number

    @staticmethod
    def is_iterator_regex(input_str: str) -> bool:
        pattern = re.compile("^<#[+\-*\/%]?\d?>$")
        return bool(pattern.match(input_str))
