import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, timedelta
from models.medicine import Medicine
from models.base import Base
from models.employee import Employee
from models.supplier import Supplier
from controllers.MedicineController import MedicineController


class TestMedicineController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Настройка БД и сессии
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        # Новая сессия для каждого теста
        self.session = self.Session()
        self.controller = MedicineController(self.session)

        # Тестовые данные
        self.test_medicine = self.controller.create_medicine(
            mname="Тестовый препарат",
            price=100.50,
            description="Тестовое описание",
            count = 5,
            category="Тестовая категория",
            bbt="2025-01-01",
            supplier_id=1
        )

    def tearDown(self):
        # Откат изменений
        self.session.rollback()
        self.session.close()

    def test_create_medicine(self):
        medicine = self.controller.create_medicine(
            mname="Аспирин",
            price=150.99,
            description="Обезболивающее",
            count = 5,
            category="Таблетки",
            bbt="2025-12-31",
            supplier_id=1
        )

        self.assertIsNotNone(medicine.id)
        self.assertEqual(medicine.MName, "Аспирин")
        self.assertAlmostEqual(float(medicine.Price), 150.99)

    def test_get_medicine_by_id(self):
        found = self.controller.get_medicine_by_id(self.test_medicine.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.MName, "Тестовый препарат")

        not_found = self.controller.get_medicine_by_id(999)
        self.assertIsNone(not_found)

    def test_update_medicine(self):
        updated = self.controller.update_medicine(
            self.test_medicine.id,
            MName="Новое название",
            Price=200.00,
            Description="Новое описание"
        )

        self.assertEqual(updated.MName, "Новое название")
        self.assertAlmostEqual(float(updated.Price), 200.00)
        self.assertEqual(updated.Description, "Новое описание")

        with self.assertRaises(ValueError):
            self.controller.update_medicine(999, MName="Несуществующий ID")

    def test_delete_medicine(self):
        result = self.controller.delete_medicine(self.test_medicine.id)
        self.assertTrue(result)

        deleted = self.controller.get_medicine_by_id(self.test_medicine.id)
        self.assertIsNone(deleted)

        result = self.controller.delete_medicine(999)
        self.assertFalse(result)

    def test_get_all_medicines(self):
        # Очистка предыдущих данных
        self.session.query(Medicine).delete()

        medicines = [
            ("Лекарство 1", "Категория А", 1),
            ("Лекарство 2", "Категория Б", 2),
            ("Лекарство 3", "Категория А", 1)
        ]

        for name, category, supplier in medicines:
            self.controller.create_medicine(
                mname=name,
                price=100,
                description="desc",
                count=5,
                category=category,
                bbt="2025-01-01",
                supplier_id=supplier
            )

        # Тест без фильтров
        all_meds = self.controller.get_all_medicines()
        self.assertEqual(len(all_meds), 3)

        # Тест фильтра по категории
        category_a = self.controller.get_all_medicines(category="Категория А")
        self.assertEqual(len(category_a), 2)

        # Тест фильтра по поставщику
        supplier_1 = self.controller.get_all_medicines(supplier_id=1)
        self.assertEqual(len(supplier_1), 2)

    def test_get_medicines_expiring_after(self):
        self.session.query(Medicine).delete()

        dates = [
            date.today() + timedelta(days=30),
            date.today() + timedelta(days=60),
            date.today() - timedelta(days=10)
        ]

        for i, exp_date in enumerate(dates):
            self.controller.create_medicine(
                mname=f"Препарат {i}",
                price=100,
                description="desc",
                count=5,
                category="test",
                bbt=exp_date.isoformat(),
                supplier_id=1
            )

        future_meds = self.controller.get_medicines_expiring_after(date.today().isoformat())
        self.assertEqual(len(future_meds), 2)

    def test_invalid_input_handling(self):
        with self.assertRaises(ValueError):
            self.controller.create_medicine(
                mname="Тест",
                price="не число",
                description="desc",
                count=5,
                category="test",
                bbt="2025-01-01",
                supplier_id=1
            )

    def test_transaction_rollback(self):
        initial_count = len(self.controller.get_all_medicines())

        with self.assertRaises(Exception):
            self.controller.create_medicine(
                mname="Тест",
                price=None,  # Некорректное значение
                description="desc",
                count=5,
                category="test",
                bbt="2025-01-01",
                supplier_id=1
            )

        final_count = len(self.controller.get_all_medicines())
        self.assertEqual(initial_count, final_count)


if __name__ == '__main__':
    unittest.main()