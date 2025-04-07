from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from typing import Optional
from models.employee import Employee
from core.security import Security

class EmployeeController:
    def __init__(self, db_session: Session):
        self.db = db_session

    # CRUD Operations
    def create_employee(self, employee_data: dict) -> Employee:
        """Создание нового сотрудника"""
        if not self.is_login_unique(employee_data['Login']):
            raise ValueError("Login already exists")

        employee_data['Pass'] = Security.get_password_hash(employee_data['Pass'])
        new_employee = Employee(**employee_data)
        self.db.add(new_employee)
        self.db.commit()
        return new_employee

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получение сотрудника по ID"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def update_employee(self, employee_id: int, update_data: dict) -> Employee:
        """Обновление данных сотрудника"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        if 'Login' in update_data and update_data['Login'] != employee.Login:
            if not self.is_login_unique(update_data['Login']):
                raise ValueError("New login already taken")

        if 'Pass' in update_data:
            update_data['Pass'] = Security.get_password_hash(update_data['Pass'])

        for key, value in update_data.items():
            setattr(employee, key, value)

        self.db.commit()
        return employee

    def delete_employee(self, employee_id: int) -> bool:
        """Удаление сотрудника"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return False

        self.db.delete(employee)
        self.db.commit()
        return True

    # Business Logic
    def authenticate(self, login: str, password: str) -> Optional[Employee]:
        """Аутентификация сотрудника"""
        employee = self.db.query(Employee).filter(Employee.Login == login).first()
        if employee and Security.verify_password(password, employee.Pass):
            return employee
        return None

    def get_experience(self, employee_id: int) -> int:
        """Получение стажа работы"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        return employee.get_experience()

    # Validation
    def is_login_unique(self, login: str) -> bool:
        """Проверка уникальности логина"""
        return not self.db.query(Employee).filter(Employee.Login == login).first()

    def get_all(self):
        """Получение всех записей"""
        return self.db.execute(select(Employee.id, Employee.FName, Employee.LName,
                                      Employee.Number, Employee.Position, Employee.Login,
                                      Employee.DTB)).all()