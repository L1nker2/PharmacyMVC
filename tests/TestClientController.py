import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.client import Client
from models.base import Base
from models.employee import Employee
from models.medicine import Medicine
from models.supplier import Supplier
from controllers.ClientController import ClientController
from core.security import Security


class TestClientController(unittest.TestCase):
    def setUp(self):
        # Настройка тестовой БД в памяти
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.controller = ClientController(self.Session())

        # Тестовые данные
        self.test_client_data = {
            'FName': 'Иван',
            'LName': 'Петров',
            'Number': '+79991234567',
            'Login': 'ivan.petrov',
            'Pass': 'strongpassword123',
            'Balance': 1000.00
        }

    def tearDown(self):
        self.Session.close_all()
        Base.metadata.drop_all(self.engine)

    def test_create_client_success(self):
        # Создание клиента
        client = self.controller.create_client(self.test_client_data)

        # Проверки
        self.assertIsInstance(client, Client)
        self.assertEqual(client.FName, 'Иван')
        self.assertTrue(Security.verify_password(
            'strongpassword123',
            client.Pass
        ))

    def test_create_client_duplicate_login(self):
        # Первое создание
        self.controller.create_client(self.test_client_data)

        # Попытка дубликата
        with self.assertRaises(ValueError) as context:
            self.controller.create_client(self.test_client_data)

        self.assertIn('Login already exists', str(context.exception))

    def test_authenticate_success(self):
        # Подготовка
        self.controller.create_client(self.test_client_data)

        # Тест
        client = self.controller.authenticate(
            'ivan.petrov',
            'strongpassword123'
        )
        self.assertIsInstance(client, Client)

    def test_authenticate_wrong_password(self):
        self.controller.create_client(self.test_client_data)

        with self.assertRaises(ValueError) as context:
            self.controller.authenticate('ivan.petrov', 'wrongpass')

        self.assertIn('Invalid password', str(context.exception))

    def test_update_balance(self):
        # Подготовка
        client = self.controller.create_client(self.test_client_data)

        # Положительное пополнение
        updated = self.controller.update_balance(client.id, 500.00)
        self.assertEqual(updated.Balance, 1500.00)

        # Отрицательное списание
        updated = self.controller.update_balance(client.id, -200.00)
        self.assertEqual(updated.Balance, 1300.00)

    def test_get_client_by_id(self):
        client = self.controller.create_client(self.test_client_data)
        found = self.controller.get_client_by_id(client.id)
        self.assertEqual(found.Login, 'ivan.petrov')

    def test_delete_client(self):
        client = self.controller.create_client(self.test_client_data)
        result = self.controller.delete_client(client.id)
        self.assertTrue(result)

        # Проверка что клиент удален
        self.assertIsNone(self.controller.get_client_by_id(client.id))


if __name__ == '__main__':
    unittest.main(verbosity=2)