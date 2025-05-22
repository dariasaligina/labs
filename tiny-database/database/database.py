from abc import ABC, abstractmethod
import csv
import os


class SingletonMeta(type):
    """ Синглтон метакласс для Database. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """ Класс-синглтон базы данных с таблицами, хранящимися в файлах. """

    def __init__(self):
        self.tables = {}

    def register_table(self, table_name, table):
        self.tables[table_name] = table

    def insert(self, table_name, data):
        table = self.tables.get(table_name)
        if table:
            table.insert(data)
        else:
            raise ValueError(f"Table {table_name} does not exist.")

    def select(self, table_name, *args):
        table = self.tables.get(table_name)
        return table.select(*args) if table else None

    def join(self, table1_name, table2_name, join_attr="id"):
        return_data = []

        for table1_entry in self.tables.get(table1_name).data:
            return_data.append(table1_entry)
            if join_attr not in table1_entry.keys():
                raise ValueError(f"invalid join_attr")

            table2_entry = self.tables.get(table2_name).find_id(table1_entry[join_attr])
            if not table2_entry:
                raise ValueError(f"{join_attr} = {table1_entry[join_attr]} does not exist.")
            for key, value in table2_entry.items():
                if key != "id":
                    return_data[-1][key] = value
        return return_data

    def aggregate(self, table_name, field_name):
        table = self.tables.get(table_name)
        if table:
            if not table.data:
                raise ValueError(f"No data in table {table_name}.")
            try:
                return_value = {"SUM": 0, "COUNT": 0, "MAX": float(table.data[0][field_name]),
                                "MIN": float(table.data[0][field_name]), }
            except:
                raise ValueError("Field must contain numbers")
            for entry in table.data:
                try:
                    n = float(entry[field_name])
                except:
                    raise ValueError("Field must contain numbers")
                return_value["SUM"] += n
                return_value['COUNT'] += 1
                return_value['MAX'] = max(return_value['MAX'], n)
                return_value["MIN"] = min(return_value["MIN"], n)
            return_value["AVG"] = return_value['SUM'] / return_value['COUNT']
            return return_value
        else:
            raise ValueError(f"Table {table_name} does not exist.")


class Table(ABC):
    """ Абстрактный бaзовый класс для таблиц с вводом/выводом файлов CSV. """

    @abstractmethod
    def insert(self, data):
        pass

    @abstractmethod
    def select(self, *args):
        pass


class EmployeeTable(Table):
    """ Таблица сотрудников с методами ввода-вывода из файла CSV. """
    ATTRS = ('id', 'name', 'age', 'salary', "department_id")
    FILE_PATH = 'employee_table.csv'

    def __init__(self):
        self.data = []
        self.load()  # Подгружаем из CSV-файла сразу при инициализации

    def insert(self, data):
        entry = dict(zip(self.ATTRS, data.split()))
        if not self.find_id(entry["id"]):
            self.data.append(entry)
            self.save()
        else:
            raise ValueError(f"Entry with id = {entry['id']} already exists.")

    def select(self, start_id, end_id):
        return [entry for entry in self.data if start_id <= int(entry['id']) <= end_id]

    def save(self):
        with open(self.FILE_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.ATTRS)
            writer.writeheader()
            writer.writerows(self.data)

    def load(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                reader = csv.DictReader(f)
                self.data = [row for row in reader]
        else:
            self.data = []

    def find_id(self, id):
        for entry in self.data:
            if entry["id"] == id:
                return entry
        return None


class DepartmentTable(Table):
    """ Таблица подразделенией с вводлм-выводом в/из CSV файла. """
    ATTRS = ('id', 'department_name')
    FILE_PATH = 'department_table.csv'

    def __init__(self):
        self.data = []
        self.load()

    # TODO: Реализовать
    def select(self, department_name):
        return [entry for entry in self.data if entry['department_name'] == department_name]

    def insert(self, data):
        entry = dict(zip(self.ATTRS, data.split()))
        if not self.find_id(entry["id"]):
            self.data.append(entry)
            self.save()
        else:
            raise ValueError(f"Entry with id = {entry['id']} already exists.")

    def save(self):
        with open(self.FILE_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.ATTRS)
            writer.writeheader()
            writer.writerows(self.data)

    def load(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                reader = csv.DictReader(f)
                self.data = [row for row in reader]
        else:
            self.data = []

    def find_id(self, id):
        for entry in self.data:
            if entry["id"] == id:
                return entry
        return None


class TemporaryTable(Table):
    def __init__(self, data):
        self.data = data
        self.ATTRS = []
        if len(self.data):
            self.ATTRS = self.data[0].keys()

    def insert(self, data):
        if not self.ATTRS:
            self.ATTRS.append("id")
            for i in range(1, len(data.split())):
                self.ATTRS.append(f"field{i}")
        entry = dict(zip(self.ATTRS, data.split()))
        if not self.find_id(entry["id"]):
            self.data.append(entry)
        else:
            raise ValueError(f"Entry with id = {entry['id']} already exists.")

    def find_id(self, id):
        for entry in self.data:
            if entry["id"] == id:
                return entry
        return None

    def select(self, field_name, field_value):
        return [entry for entry in self.data if entry[field_name] == field_value]


class BonusTable(Table):
    """ Таблица подразделенией с вводлм-выводом в/из CSV файла. """
    ATTRS = ('id', 'employee_id', "date", 'amount')
    FILE_PATH = 'bonus_table.csv'

    def __init__(self):
        self.data = []
        self.load()

    def insert(self, data):
        entry = dict(zip(self.ATTRS, data.split()))
        if not self.find_id(entry["id"]):
            self.data.append(entry)
            self.save()
        else:
            raise ValueError(f"Entry with id = {entry['id']} already exists.")

    def save(self):
        with open(self.FILE_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.ATTRS)
            writer.writeheader()
            writer.writerows(self.data)

    def load(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                reader = csv.DictReader(f)
                self.data = [row for row in reader]
        else:
            self.data = []

    def find_id(self, id):
        for entry in self.data:
            if entry["id"] == id:
                return entry
        return None

    def select(self, employee_id):
        return [entry for entry in self.data if int(entry['employee_id']) == employee_id]
