from typing import Optional, Type, Any
import sqlalchemy
from sqlalchemy import Row
from sqlalchemy.orm import Session

from core.security import Security
from models.employee import Employee


class EmployeeController:
    def __init__(self, db_session: Session):
        """Инициализация контроллера с сессией базы данных."""
        self.db = db_session

    def create_employee(self, employee_data: dict) -> Employee:
        """Создает нового сотрудника (Employee) с хешированием пароля."""
        # Отдельно обработаем пароль: захешируем его перед сохранением
        if employee_data['FName'] == '' or employee_data['LName'] == '' \
            or employee_data['Number'] == '' or employee_data['Position'] == ''\
            or employee_data['Login'] == '' or employee_data['Pass'] == '' \
            or employee_data['DTB'] == '' or employee_data['Admin'] == '':
            raise ValueError("Fill in all fields")

        if not self.is_login_unique(employee_data['Login']):
            raise sqlalchemy.exc.IntegrityError(statement="UNIQUE constraint failed", params="UNIQUE constraint failed", orig="UNIQUE constraint failed")
        password_plain = employee_data.get("Pass")
        if password_plain is not None:
            # Заменяем открытый пароль на его хеш
            employee_data["Pass"] = Security.get_password_hash(password_plain)
        # Создаем объект модели Employee
        employee = Employee(**employee_data)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)  # Обновляем объект, чтобы получить сгенерированный ID и др.
        return employee

    def get_employee_by_id(self, employee_id: int) -> Type[Employee]:
        """Возвращает сотрудника по ID или None, если не найден."""
        employee = self.db.get(Employee, employee_id)
        if employee is None:
            raise ValueError("Employee not found")
        else: return employee
        # Альтернатива: query + filter + first

    def update_employee(self, employee_id: int, update_data: dict) -> Type[Employee] | None:
        """Обновляет данные сотрудника по ID и возвращает обновленный объект или None."""
        employee = self.db.get(Employee, employee_id)
        if not employee:
            raise ValueError("Employee not found")

        if update_data['FName'] == '' or update_data['LName'] == '' \
            or update_data['Number'] == '' or update_data['Position'] == ''\
            or update_data['Login'] == '' \
            or update_data['DTB'] == '' or update_data['Admin'] == '':
            raise ValueError("Fill in all fields")
        # Если в обновлении присутствует новый пароль, захешировать его
        if "Pass" in update_data:
            update_data["Pass"] = Security.get_password_hash(update_data["Pass"])
        # Обновляем указанные поля
        for field, value in update_data.items():
            setattr(employee, field, value)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete_employee(self, employee_id: int) -> Type[Employee] | None:
        """Удаляет сотрудника по ID. Возвращает удалённый объект или None, если не найден."""
        employee = self.db.get(Employee, employee_id)
        if not employee:
            raise ValueError("Employee not found")
        self.db.delete(employee)
        self.db.commit()
        return employee

    def get_all(self) -> list[Row[tuple[Any, Any, Any, Any, Any, Any, Any, Any]]]:
        """Возвращает список всех сотрудников (ограниченный набор полей для эффективности)."""
        # Используем load_only, чтобы загрузить только нужные поля (например, id, name, login)
        employees = (
            self.db.query(
                Employee.id,
                Employee.FName,
                Employee.LName,
                Employee.Number,
                Employee.Login,
                Employee.Pass,
                Employee.DTB,
                Employee.Position,
                Employee.Admin,
            )
            .all()
        )
        return employees
        # Примечание: load_only загрузит только указанные столбцы и первичный ключ

    def authenticate(self, login: str, password: str) -> Type[Employee] | None:
        """Аутентифицирует сотрудника по логину и паролю. Возвращает объект Employee или None."""
        # Ищем сотрудника по логину
        employee = self.db.query(Employee).filter(Employee.Login == login).first()
        if not employee:
            return None
        # Проверяем пароль с помощью Security (сравнение хеша пароля)
        if Security.verify_password(password, str(employee.Pass)):
            return employee
        return None

    def get_experience(self, employee_id: int) -> Optional[int]:
        """Вычисляет стаж сотрудника (в годах) на основе даты найма."""
        employee = self.db.get(Employee, employee_id)
        if not employee:
            return None
        if hasattr(employee, "hire_date") and employee.hire_date:
            # Рассчитываем разницу между сегодня и датой найма в днях, переводим в годы
            from datetime import date
            delta = date.today() - employee.hire_date
            years = delta.days // 365
            return years
        return 0  # Если дата найма не указана, стаж 0

    def is_login_unique(self, login: str) -> bool:
        """Проверяет, уникален ли указанный логин (True, если такого логина нет в базе)."""
        existing = self.db.query(Employee).filter(Employee.Login == login).first()
        return existing is None
