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


def test_aggregate_nonexistent_table(database):
    with pytest.raises(ValueError, match="Table non_existent_table does not exist."):
        database.aggregate("non_existent_table", "age")


def test_aggregate_empty_table(database):
    with pytest.raises(ValueError, match="No data in table employees."):
        database.aggregate("employees", "age")


def test_aggregate_non_numeric_field(database):
    database.insert("employees", "1 Alice 30 70000 1")
    with pytest.raises(ValueError, match="Field must contain numbers"):
        database.aggregate("employees", "name")


def test_invalid_join_attr(database):
    database.insert("employees", "1 Alice 30 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")
    database.insert("departments", "1 Security")
    database.insert("departments", "2 Engineering")
    with pytest.raises(ValueError, match="invalid join_attr"):
        database.join("employees", "departments", "abc")


def test_table2_entry_nonexistent(database):
    database.insert("employees", "1 Alice 30 70000 5")
    database.insert("departments", "1 Security")
    with pytest.raises(ValueError, match="department_id = 5 does not exist."):
        database.join("employees", "departments", "department_id")


def test_invalid_aggregate(database):
    database.insert("employees", "1 Alice a 70000 1")
    database.insert("employees", "2 Bob 28 60000 2")
    with pytest.raises(ValueError, match="Field must contain numbers"):
        database.aggregate("employees", "age")


def test_invalid_insert(database):
    database.insert("employees", "1 Alice a 70000 1")
    with pytest.raises(ValueError, match="Entry with id = 1 already exists."):
        database.insert("employees", "1 Bob 28 60000 2")


def test_employee_table_insert_duplicate_id(database):
    database.insert("employees", "4 David 35 80000 3")
    with pytest.raises(ValueError, match="Entry with id = 4 already exists."):
        database.insert("employees", "4 Eve 25 50000 4")


def test_department_table_insert_duplicate_id(database):
    database.insert("departments", "4 Marketing")
    with pytest.raises(ValueError, match="Entry with id = 4 already exists."):
        database.insert("departments", "4 Sales")


def test_bonus_table_insert_duplicate_id(database):
    database.insert("bonuses", "4 5 13.05.2024 6000")
    with pytest.raises(ValueError, match="Entry with id = 4 already exists."):
        database.insert("bonuses", "4 6 14.06.2024 7000")


def test_employee_table_select_range(database):
    database.insert("employees", "5 Frank 40 90000 1")
    database.insert("employees", "6 Grace 32 75000 2")
    database.insert("employees", "7 Heidi 28 65000 1")
    selected_employees = database.select("employees", 5, 6)
    assert len(selected_employees) == 2
    assert selected_employees[0] == {'id': '5', 'name': 'Frank', 'age': '40', 'salary': '90000', "department_id": "1"}
    assert selected_employees[1] == {'id': '6', 'name': 'Grace', 'age': '32', 'salary': '75000', "department_id": "2"}


def test_department_table_save_load(database, temp_department_file):
    department_table = DepartmentTable()
    department_table.FILE_PATH = temp_department_file
    database.register_table("departments", department_table)
    database.insert("departments", "8 R&D")
    database.insert("departments", "9 QA")
    # Создаем новый экземпляр DepartmentTable, чтобы проверить загрузку данных
    new_department_table = DepartmentTable()
    new_department_table.FILE_PATH = temp_department_file
    new_department_table.load()
    assert len(new_department_table.data) == 2
    assert new_department_table.data[0] == {'id': '8', 'department_name': 'R&D'}
    assert new_department_table.data[1] == {'id': '9', 'department_name': 'QA'}


def test_employee_table_save_load(database, temp_employee_file):
    employee_table = EmployeeTable()
    employee_table.FILE_PATH = temp_employee_file
    database.register_table("employees", employee_table)
    database.insert("employees", "8 John 40 90000 3")
    database.insert("employees", "9 Alex 32 75000 2")
    new_employee_table = EmployeeTable()
    new_employee_table.FILE_PATH = temp_employee_file
    new_employee_table.load()
    assert len(new_employee_table.data) == 2
    assert new_employee_table.data[0] == {'id': '8', 'name': 'John', 'age': '40', 'salary': '90000',
                                          "department_id": "3"}
    assert new_employee_table.data[1] == {'id': '9', 'name': 'Alex', 'age': '32', 'salary': '75000',
                                          "department_id": "2"}


def test_bonus_table_save_load(database, temp_bonus_file):
    bonus_table = BonusTable()
    bonus_table.FILE_PATH = temp_bonus_file
    database.register_table("bonuses", bonus_table)
    database.insert("bonuses", "5 10 15.07.2024 8000")
    database.insert("bonuses", "6 11 16.08.2024 9000")
    new_bonus_table = BonusTable()
    new_bonus_table.FILE_PATH = temp_bonus_file
    new_bonus_table.load()
    assert len(new_bonus_table.data) == 2
    assert new_bonus_table.data[0] == {'id': '5', 'employee_id': '10', 'date': '15.07.2024', 'amount': '8000'}
    assert new_bonus_table.data[1] == {'id': '6', 'employee_id': '11', 'date': '16.08.2024', 'amount': '9000'}
