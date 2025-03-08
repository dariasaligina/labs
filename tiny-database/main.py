from database.database import Database, EmployeeTable, DepartmentTable,BonusTable, TemporaryTable

if __name__ == "__main__":
    db = Database()

    # Создание таблиц в базе данных
    db.register_table("employees", EmployeeTable())
    db.register_table("departments", DepartmentTable())
    db.register_table("bonuses", BonusTable())






    ans = db.aggregate('bonuses','amount')
    print(ans)




    # Проверяем вставку, подгружая с CSV

