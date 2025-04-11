import pytest
from datetime import datetime
import sqlalchemy
from controllers.EmployeeController import EmployeeController
from models.employee import Employee  # ORM-модель сотрудника

def test_create_employee_success(session):
    controller = EmployeeController(session)
    # Выполняем создание сотрудника с валидными данными
    test_data = {
        'FName' : "John",
        'LName' : "Doe",
        'Number': "+79999999999",
        'Position': "Manager",
        'Login' : "john@example.com",
        'Pass' : "testPassword",
        'DTB' : datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin' : True
    }
    new_emp = controller.create_employee(test_data)
    # new_emp – возвращенный объект Employee (предположительно ORM-модель или DTO)
    assert new_emp.id is not None, "После создания у сотрудника должен появиться ID"
    # Проверяем, что объект сохранен в базе через сессию
    emp_from_db = session.query(Employee).get(new_emp.id)
    assert emp_from_db is not None
    assert emp_from_db.FName == "John"
    assert emp_from_db.LName == "Doe"
    assert emp_from_db.Number == "+79999999999"
    assert emp_from_db.Position == "Manager"
    assert emp_from_db.Login == "john@example.com"
    assert emp_from_db.DTB == datetime.strptime('1999-12-31', '%Y-%m-%d').date()
    assert emp_from_db.Admin == True

def test_get_employee_by_id(session):
    test_data = {
        'FName': "Alice",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "Manager",
        'Login': "alice@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime("1999-12-31", '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    # Предварительно создаем сотрудника (воспользуемся методом контроллера)
    emp = controller.create_employee(test_data)
    emp_id = emp.id
    # Получаем сотрудника по ID
    fetched = controller.get_employee_by_id(emp_id)
    assert fetched is not None
    assert fetched.id == emp_id
    assert fetched.FName == "Alice"
    assert fetched.LName == "Doe"
    assert fetched.Number == "+79999999999"
    assert fetched.Position == "Manager"
    assert fetched.Login == "alice@example.com"
    assert fetched.DTB == datetime.strptime('1999-12-31', '%Y-%m-%d').date()
    assert fetched.Admin == True

def test_get_employee_not_found(session):
    controller = EmployeeController(session)
    # Ищем сотрудника по несуществующему ID
    with pytest.raises(Exception):  # Ожидаем какое-то исключение, например ValueError или кастомное
        controller.get_employee_by_id(9999)

def test_create_employee_missing_name(session):
    test_data = {
        'FName': "",
        'LName': "",
        'Number': "+79999999999",
        'Position': "Engineer",
        'Login': "alice@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    # Попытка создать сотрудника без имени (обязательное поле)
    with pytest.raises(ValueError):
        controller.create_employee(test_data)

def test_create_employee_duplicate_email(session):
    test_data = {
        'FName': "Bob",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "Technician",
        'Login': "bob@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    test_data2 = {
        'FName': "Robert",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "Analyst",
        'Login': "bob@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    # Сначала успешно создаем сотрудника с определенным email
    controller.create_employee(test_data)
    # Повторное создание с таким же email должно нарушить уникальность email
    with pytest.raises(sqlalchemy.exc.IntegrityError) as excinfo:
        controller.create_employee(test_data2)
    # Проверяем, что текст ошибки указывает на нарушение уникального ограничения email
    assert "UNIQUE constraint failed" in str(excinfo.value)  # обычно содержит имя таблицы и столбца

def test_update_employee_success(session):
    test_data = {
        'FName': "Charlie",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "DevOps",
        'Login': "charlie@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    emp = controller.create_employee(test_data)
    emp_id = emp.id
    # Обновляем некоторые поля сотрудника
    updated_data = {
        'FName': "Charlie",
        'LName': "C.",
        'Number': "+79999999999",
        'Position': "Senior DevOps",
        'Login': "alice@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    updated = controller.update_employee(emp_id, updated_data)
    # Проверяем, что возвращенный обновленный объект имеет новые данные
    assert updated.FName == "Charlie"
    assert updated.LName == "C."
    assert updated.Position == "Senior DevOps"
    # Дополнительно проверяем непосредственно через ORM, что изменения сохранены
    emp_from_db = session.query(Employee).get(emp_id)
    assert emp_from_db.FName == "Charlie"
    assert emp_from_db.LName == "C."
    assert emp_from_db.Position == "Senior DevOps"

def test_update_employee_not_found(session):
    controller = EmployeeController(session)
    test_data = {
        'FName': "Alice",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "Engineer",
        'Login': "alice@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    # Обновление несуществующего ID
    with pytest.raises(Exception):  # Ожидаем исключение (например, NotFoundError)
        controller.update_employee(12345, test_data)

def test_update_employee_invalid_data(session):
    test_data = {
        'FName': "Daisy",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "HR",
        'Login': "daisy@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    emp = controller.create_employee(test_data)
    # Попытка обновить сотрудника недопустимыми данными (например, пустое имя)
    updated_data = {
        'FName': "",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "HR",
        'Login': "daisy@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    with pytest.raises(ValueError):
        controller.update_employee(emp.id, updated_data)

def test_delete_employee_success(session):
    test_data = {
        'FName': "Eve",
        'LName': "Doe",
        'Number': "+79999999999",
        'Position': "QA",
        'Login': "eve@example.com",
        'Pass': "testPassword",
        'DTB': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Admin': True
    }
    controller = EmployeeController(session)
    emp = controller.create_employee(test_data)
    emp_id = emp.id
    # Удаляем существующего сотрудника
    controller.delete_employee(emp_id)
    # Проверяем, что сотрудника больше нет в базе
    assert session.query(Employee).get(emp_id) is None

def test_delete_employee_not_found(session):
    controller = EmployeeController(session)
    # Удаление несуществующего сотрудника должно вызвать исключение
    with pytest.raises(Exception):
        controller.delete_employee(9999)
