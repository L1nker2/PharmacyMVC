import unittest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.employee import Employee
from models.medicine import Medicine
from models.supplier import Supplier
from models.base import Base
from controllers.EmployeeController import EmployeeController
from core.security import Security


class TestEmployeeController(unittest.TestCase):
    def setUp(self):
        # Настройка тестовой БД в памяти
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.controller = EmployeeController(self.Session())

        # Тестовые данные
        self.test_data = {
            'FName': 'Иван',
            'LName': 'Петров',
            'Number': '+79991234567',
            'Position': 'Кассир',
            'Login': 'ivan.p',
            'Pass': 'strongpass123',
            'DTB': date(2020, 5, 15)
        }

    def tearDown(self):
        self.Session.close_all()
        Base.metadata.drop_all(self.engine)

    def test_create_employee_success(self):
        employee = self.controller.create_employee(self.test_data)
        self.assertIsInstance(employee, Employee)
        self.assertEqual(employee.Position, 'Кассир')
        self.assertTrue(Security.verify_password(
            'strongpass123',
            employee.Pass
        ))

    def test_create_duplicate_login(self):
        self.controller.create_employee(self.test_data)
        with self.assertRaises(ValueError) as context:
            self.controller.create_employee(self.test_data)
        self.assertIn('Login already exists', str(context.exception))

    def test_get_employee_by_id(self):
        created = self.controller.create_employee(self.test_data)
        found = self.controller.get_employee_by_id(created.id)
        self.assertEqual(found.Login, 'ivan.p')

    def test_update_employee(self):
        # Создание и обновление
        employee = self.controller.create_employee(self.test_data)
        updated = self.controller.update_employee(employee.id, {
            'Position': 'Старший кассир',
            'Number': '+79998765432'
        })
        self.assertEqual(updated.Position, 'Старший кассир')
        self.assertEqual(updated.Number, '+79998765432')

    def test_update_password(self):
        employee = self.controller.create_employee(self.test_data)
        new_password = 'new_strong_pass'
        updated = self.controller.update_employee(employee.id, {
            'Pass': new_password
        })
        self.assertTrue(Security.verify_password(
            new_password,
            updated.Pass
        ))

    def test_delete_employee(self):
        employee = self.controller.create_employee(self.test_data)
        result = self.controller.delete_employee(employee.id)
        self.assertTrue(result)
        self.assertIsNone(self.controller.get_employee_by_id(employee.id))

    def test_authenticate_success(self):
        self.controller.create_employee(self.test_data)
        employee = self.controller.authenticate('ivan.p', 'strongpass123')
        self.assertIsInstance(employee, Employee)

    def test_authenticate_failure(self):
        self.controller.create_employee(self.test_data)
        self.assertIsNone(self.controller.authenticate('ivan.p', 'wrongpass'))
        self.assertIsNone(self.controller.authenticate('wronglogin', 'strongpass123'))

    def test_get_experience(self):
        today = date.today()

        # Точная дата 3 года назад
        test_date = date(today.year - 3, today.month, today.day)
        self.test_data['DTB'] = test_date
        employee = self.controller.create_employee(self.test_data)
        self.assertEqual(self.controller.get_experience(employee.id), 3)
        self.controller.delete_employee(employee.id)

        # На 1 день раньше 3-летней отметки
        test_date = date(today.year - 3, today.month, today.day) - timedelta(days=1)
        self.test_data['DTB'] = test_date
        employee = self.controller.create_employee(self.test_data)
        self.assertEqual(self.controller.get_experience(employee.id), 3)
        self.controller.delete_employee(employee.id)

        # На 1 день позже 3-летней отметки
        test_date = date(today.year - 3, today.month, today.day) + timedelta(days=1)
        self.test_data['DTB'] = test_date
        employee = self.controller.create_employee(self.test_data)
        self.assertEqual(self.controller.get_experience(employee.id), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)