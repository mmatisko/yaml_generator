import csv
from abc import abstractmethod, ABC
from dynamic_value import DynamicValue
from random import randint
from os.path import isfile


class ListFileReader(DynamicValue):
    class __AbstractReader(ABC):
        @abstractmethod
        def get_item_count(self):
            pass

        @abstractmethod
        def read_value(self, index: int):
            pass

    class __CsvReader(__AbstractReader):
        def __init__(self, path: str):
            self.__path = path
            self.__item_count = -1
            self.__dialect = None
            with open(path, 'r') as detected_file:
                try:
                    dialect = csv.Sniffer().sniff(detected_file.read(32))
                    self.__dialect = dialect
                    detected_file.seek(0)
                except csv.Error:
                    raise

        def get_item_count(self):
            if self.__item_count is -1:
                self.__item_count = 0
                with open(self.__path, "r") as f:
                    reader = csv.reader(f, dialect=self.__dialect, delimiter=self.__dialect.delimiter)
                    for row in reader:
                        self.__item_count += len(row)
            return self.__item_count

        def read_value(self, index: int):
            with open(self.__path, "r") as f:
                reader = csv.reader(f, dialect=self.__dialect, delimiter=self.__dialect.delimiter)
                counter: int = 0
                for row in reader:
                    if (counter + len(row)) <= index:
                        counter += len(row)
                    else:
                        return row[index - counter]

    class __SingleLineItemReader(__AbstractReader):
        def __init__(self, path):
            self.__path = path
            self.__item_count = -1
            with open(path, 'r') as detected_file:
                line = detected_file.readline()
                if ' ' in line or not line.endswith('\n'):
                    raise ValueError

        def get_item_count(self):
            if self.__item_count is not -1:
                return self.__item_count
            else:
                with open(self.__path, 'r') as read_file:
                    line_index = 0
                    while read_file.readline() is not '':
                        line_index += 1
                return line_index

        def read_value(self, index: int):
            with open(self.__path, 'r') as read_file:
                for i in range(0, index):
                    _ = read_file.readline()
                return read_file.readline().strip()

    def __init__(self, path: str):
        self.__used_items: set = set()
        self.__reader: ListFileReader.__AbstractReader = None
        try:
            if not isfile(path):
                raise ValueError
            self._detect_type(path)
        except Exception:
            raise

    def _detect_type(self, path):
        if not (path.endswith('.txt') or path.endswith('.csv')):
            return

        try:
            self.__reader = ListFileReader.__CsvReader(path)
        except Exception:
            try:
                self.__reader = ListFileReader.__SingleLineItemReader(path)
            except Exception:
                raise

    @property
    def reader(self):
        return self.__reader

    @property
    def is_valid(self) -> bool:
        return self.__reader is not None

    def get_random_value(self) -> str:
        item_count: int = self.__reader.get_item_count()
        random_item: int = -1
        while random_item == -1 or random_item in self.__used_items:
            random_item = randint(0, item_count - 1)
        self.__used_items.add(random_item)
        return self.__reader.read_value(random_item)
