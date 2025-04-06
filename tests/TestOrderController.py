import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from models.base import Base
from models.order import Order
from models.client import Client
from models.employee import Employee
from models.supplier import Supplier
from models.medicine import Medicine
from controllers.OrderController import OrderController
from controllers.ClientController import ClientController
from controllers.EmployeeController import EmployeeController


class TestOrderController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.session = self.Session()
        self.controller = OrderController(self.session)
        self.client_controller = ClientController(self.session)
        self.employee_controller = EmployeeController(self.session)

        # Создаем тестовые данные
        test_client_data = {
            'FName': 'Иван',
            'LName': 'Петров',
            'Number': '+79991234567',
            'Login': 'ivan.petrov',
            'Pass': 'strongpassword123',
            'Balance': 1000.00
        }
        test_employee_data = {
            'FName': 'Костик',
            'LName': 'Петров',
            'Number': '+79991234567',
            'Position': 'Кассир',
            'Login': 'ivan.p',
            'Pass': 'strongpass123',
            'DTB': date(2020, 5, 15)
        }
        self.client = self.client_controller.create_client(client_data=test_client_data)
        self.employee = self.employee_controller.create_employee(employee_data=test_employee_data)
        self.session.add_all([self.client, self.employee])
        self.session.commit()

        # Тестовый заказ
        self.test_order = self.controller.create_order(
            date_reg=date(2023, 1, 1),
            amount=1000.00,
            status="New",
            client_id=1,
            employee_id=1
        )

    def tearDown(self):
        self.client_controller.delete_client(self.client.id)
        self.employee_controller.delete_employee(self.employee.id)
        orders = self.controller.get_all_orders()
        for order in orders:
            self.controller.delete_order(order.id)
        self.session.rollback()
        self.session.close()

    def test_create_order_success(self):
        order = self.controller.create_order(
            date_reg=date.today(),
            amount=2000.00,
            status="Processing",
            client_id=1,
            employee_id=1
        )

        self.assertIsNotNone(order.id)
        self.assertEqual(order.Amount, 2000.00)
        self.assertEqual(order.Status, "Processing")

    def test_create_order_invalid_data(self):
        with self.assertRaises(ValueError):
            self.controller.create_order(
                date_reg="invalid-date",
                amount=1000.00,
                status="New",
                client_id=1,
                employee_id=1
            )

    def test_get_order_by_id(self):
        order = self.controller.get_order_by_id(self.test_order.id)
        self.assertEqual(order.Amount, 1000.00)

        missing_order = self.controller.get_order_by_id(999)
        self.assertIsNone(missing_order)

    def test_get_order_with_relations(self):
        order = self.controller.get_order_by_id(self.test_order.id, include_relations=True)
        self.assertEqual(order.client.FName, "Иван")
        self.assertEqual(order.employee.FName, "Костик")

    def test_update_order(self):
        updated = self.controller.update_order(
            self.test_order.id,
            Status="Completed",
            Amount=1500.00
        )

        self.assertEqual(updated.Status, "Completed")
        self.assertEqual(updated.Amount, 1500.00)

    def test_update_nonexistent_order(self):
        with self.assertRaises(ValueError):
            self.controller.update_order(999, Status="Cancelled")

    def test_delete_order(self):
        result = self.controller.delete_order(self.test_order.id)
        self.assertTrue(result)

        result = self.controller.delete_order(999)
        self.assertFalse(result)

    def test_get_all_orders_filtering(self):
        # Создаем дополнительные заказы
        self.controller.create_order(
            date_reg=date(2023, 1, 2),
            amount=2000.00,
            status="Processing",
            client_id=1,
            employee_id=1
        )

        # Тест без фильтров
        orders = self.controller.get_all_orders()
        self.assertEqual(len(orders), 2)

        # Фильтр по статусу
        new_orders = self.controller.get_all_orders(status="New")
        self.assertEqual(len(new_orders), 1)

        # Фильтр по дате
        start_date = date(2023, 1, 2)
        end_date = date(2023, 1, 3)
        date_filtered = self.controller.get_all_orders(
            start_date=start_date,
            end_date=end_date
        )
        self.assertEqual(len(date_filtered), 1)

    def test_order_statistics(self):
        # Добавляем еще заказов
        self.controller.create_order(
            date_reg=date.today(),
            amount=2000.00,
            status="Completed",
            client_id=1,
            employee_id=1
        )

        stats = self.controller.get_order_statistics()

        self.assertEqual(stats['total_orders'], 2)
        self.assertAlmostEqual(stats['total_amount'], 3000.00)
        self.assertAlmostEqual(stats['average_order'], 1500.00)

    def test_empty_statistics(self):
        self.session.query(Order).delete()
        stats = self.controller.get_order_statistics()

        self.assertEqual(stats['total_orders'], 0)
        self.assertEqual(stats['total_amount'], 0.0)
        self.assertEqual(stats['average_order'], 0.0)

    def test_status_transition(self):
        updated = self.controller.update_order_status(
            self.test_order.id,
            "Shipped"
        )
        self.assertEqual(updated.Status, "Shipped")

    def test_date_range_queries(self):
        orders = self.controller.get_all_orders()
        for order in orders:
            self.controller.delete_order(order.id)
        # Создаем заказы с разными датами
        dates = [
            date(2023, 1, 1),
            date(2023, 1, 15),
            date(2023, 2, 1)
        ]

        for d in dates:
            self.controller.create_order(
                date_reg=d,
                amount=100.00,
                status="Test",
                client_id=1,
                employee_id=1
            )

        # Тестируем диапазон
        start = date(2023, 1, 1)
        end = date(2023, 1, 31)
        orders = self.controller.get_orders_in_date_range(start_date=start, end_date=end)
        self.assertEqual(len(orders), 2)

    def test_transaction_rollback(self):
        initial_count = self.controller.get_order_statistics()['total_orders']

        try:
            self.controller.create_order(
                date_reg=date.today(),
                amount="invalid-amount",
                status="New",
                client_id=1,
                employee_id=1
            )
        except ValueError:
            pass

        new_count = self.controller.get_order_statistics()['total_orders']
        self.assertEqual(initial_count, new_count)


if __name__ == '__main__':
    unittest.main(verbosity=2)