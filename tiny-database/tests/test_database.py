import pytest
import os
import tempfile
from database.database import Database, EmployeeTable, DepartmentTable, BonusTable, TemporaryTable


@pytest.fixture
def temp_employee_file():
    """ Создаем временный файл для таблицы рабочих """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    yield temp_file.name
    try:
        os.remove(temp_file.name)  # Удаляем временный файл после завершения теста
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")


@pytest.fixture
def temp_department_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    yield temp_file.name
    try:
        os.remove(temp_file.name)  # Удаляем временный файл после завершения теста
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")


@pytest.fixture
def temp_bonus_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    yield temp_file.name
    try:
        os.remove(temp_file.name)  # Удаляем временный файл после завершения теста
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")


# Пример, как используются фикстуры
@pytest.fixture
def database(temp_employee_file, temp_department_file, temp_bonus_file):
    """ Данная фикстура задает БД и определяет таблицы. """
    db = Database()

    # Используем временные файлы для тестирования файлового ввода-вывода в EmployeeTable и DepartmentTable
    employee_table = EmployeeTable()
    employee_table.FILE_PATH = temp_employee_file
    department_table = DepartmentTable()
    department_table.FILE_PATH = temp_department_file
    bonus_table = BonusTable()
    bonus_table.FILE_PATH = temp_bonus_file

    db.register_table("employees", employee_table)
    db.register_table("departments", department_table)
    db.register_table("bonuses", bonus_table)

    return db


def test_insert_employee(database):
    database.insert("employees", "1 Alice 30 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")

    # Проверяем вставку, подгружая с CSV
    employee_data = database.select("employees", 1, 2)
    print(employee_data)
    assert len(employee_data) == 2
    assert employee_data[0] == {'id': '1', 'name': 'Alice', 'age': '30', 'salary': '70000', "department_id": "1"}
    assert employee_data[1] == {'id': '2', 'name': 'Bob', 'age': '28', 'salary': '60000', "department_id": "2"}


def test_insert_department(database):
    database.insert("departments", "1 Security")
    database.insert("departments", "2 Engineering")
    database.insert("departments", "3 Security")

    # Проверяем вставку, подгружая с CSV
    department_data = database.select("departments", "Security")
    assert len(department_data) == 2
    assert department_data[0] == {'id': '1', 'department_name': "Security"}
    assert department_data[1] == {'id': '3', 'department_name': "Security"}

    department_data = database.select("departments", "Engineering")
    assert len(department_data) == 1
    assert department_data[0] == {'id': '2', 'department_name': "Engineering"}
    department_data = database.select("departments", "abc")
    assert len(department_data) == 0


def test_join_employees_departments(database):
    database.insert("employees", "1 Alice 30 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")
    database.insert("departments", "1 Security")
    database.insert("departments", "2 Engineering")

    # Проверяем вставку, подгружая с CSV
    employee_data = database.join("employees", "departments", "department_id")

    assert len(employee_data) == 2
    assert employee_data[0] == {'id': '1', 'name': 'Alice', 'age': '30', 'salary': '70000', "department_id": "1",
                                'department_name': "Security"}
    assert employee_data[1] == {'id': '2', 'name': 'Bob', 'age': '28', 'salary': '60000', "department_id": "2",
                                'department_name': "Engineering"}


def test_insert_bonus(database):
    database.insert("bonuses", "1 1 10.02.2025 5000")
    database.insert("bonuses", "2 3 11.03.2024 10000")

    bonus_data = database.select("bonuses", 1)
    assert len(bonus_data) == 1
    assert bonus_data[0] == {'id': '1', 'employee_id': '1', 'date': '10.02.2025', 'amount': '5000'}

    bonus_data = database.select("bonuses", 3)
    assert len(bonus_data) == 1
    assert bonus_data[0] == {'id': '2', 'employee_id': '3', 'date': '11.03.2024', 'amount': '10000'}

    bonus_data = database.select("bonuses", 2)
    assert len(bonus_data) == 0


def test_join_3_tables(database):
    database.insert("employees", "1 Alice 30 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")
    database.insert("departments", "1 Security")
    database.insert("departments", "2 Engineering")
    database.insert("bonuses", "1 1 10.02.2025 5000")
    database.insert("bonuses", "2 2 11.03.2024 10000")

    employee_data = database.join("employees", "departments", "department_id")

    database.register_table("temporary", TemporaryTable(employee_data))
    join_all = database.join("bonuses", "temporary", "employee_id")
    print(join_all)


def test_agrigate(database):
    database.insert("employees", "1 Alice 30 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")
    aggregate_result = database.aggregate("employees", "age")
    assert aggregate_result == {'SUM': 58.0, 'COUNT': 2, 'MAX': 30.0, 'MIN': 28.0, 'AVG': 29.0}
    aggregate_result = database.aggregate("employees", "salary")
    assert aggregate_result == {'SUM': 130000.0, 'COUNT': 2, 'MAX': 70000.0, 'MIN': 60000.0, 'AVG': 65000.0}

def test_insert_nonexistent_table(database):
    with pytest.raises(ValueError, match="Table non_existent_table does not exist."):
        database.insert("non_existent_table", "1 John 30 50000")
