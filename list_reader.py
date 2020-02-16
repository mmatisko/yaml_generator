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
            self.path = path
            self.item_count = -1
            self.dialect = None
            with open(path, 'r') as detected_file:
                try:
                    dialect = csv.Sniffer().sniff(detected_file.read(32))
                    self.dialect = dialect
                    detected_file.seek(0)
                except csv.Error as e:
                    raise

        def get_item_count(self):
            if self.item_count is -1:
                self.item_count = 0
                with open(self.path, "r") as f:
                    reader = csv.reader(f, dialect=self.dialect, delimiter=self.dialect.delimiter)
                    for row in reader:
                        self.item_count += len(row)
            return self.item_count

        def read_value(self, index: int):
            with open(self.path, "r") as f:
                reader = csv.reader(f, dialect=self.dialect, delimiter=self.dialect.delimiter)
                counter: int = 0
                for row in reader:
                    if (counter + len(row)) <= index:
                        counter += len(row)
                    else:
                        return row[index - counter]

    class __SingleLineItemReader(__AbstractReader):
        def __init__(self, path):
            self.path = path
            self.item_count = -1
            with open(path, 'r') as detected_file:
                line = detected_file.readline()
                if ' ' in line or not line.endswith('\n'):
                    raise ValueError

        def get_item_count(self):
            if self.item_count is not -1:
                return self.item_count
            else:
                with open(self.path, 'r') as read_file:
                    line_index = 0
                    while read_file.readline() is not '':
                        line_index += 1
                return line_index

        def read_value(self, index: int):
            with open(self.path, 'r') as read_file:
                for i in range(0, index):
                    _ = read_file.readline()
                return read_file.readline().strip()

    def __init__(self, path: str):
        self.used_items: set = set()
        self.reader: ListFileReader.__AbstractReader = None
        try:
            if not isfile(path):
                raise ValueError
            self.__detect_type(path)
        except Exception:
            raise

    def __detect_type(self, path):
        if not path.endswith('.txt') and not path.endswith('logins.csv'):
            return

        try:
            self.reader = ListFileReader.__CsvReader(path)
        except Exception as a:
            try:
                self.reader = ListFileReader.__SingleLineItemReader(path)
            except Exception:
                raise

    @property
    def is_valid(self) -> bool:
        return self.reader is not None

    def get_random_value(self) -> str:
        item_count: int = self.reader.get_item_count()
        random_item: int = -1
        while random_item == -1 or random_item in self.used_items:
            random_item = randint(0, item_count - 1)
        self.used_items.add(random_item)
        return self.reader.read_value(random_item)
