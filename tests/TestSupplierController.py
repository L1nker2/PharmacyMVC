import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.employee import Employee
from models.medicine import Medicine
from models.supplier import Supplier
from controllers.SupplierController import SupplierController


class TestSupplierController(unittest.TestCase):
    def setUp(self):
        # Создаем новую in-memory SQLite базу для каждого теста
        self.engine = create_engine('sqlite:///:memory:')
        """
        С sqllite проваливается тест поиска записи, там нет неточного поиска
        поэтому дополнительно стоит тестировать в прод ДБ!
        self.engine = create_engine("mysql+mysqldb://python:python@localhost/apteka",
                                    pool_recycle=3600,
                                    echo=False)
        """
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        # Создаем экземпляр контроллера, передавая сессию
        self.controller = SupplierController(self.session)

        # Создаем тестового поставщика для использования в тестах
        self.supplier = self.controller.create_supplier(
            comp_name="Тестовая компания",
            address="Тестовый адрес",
            phone="+71234567890",
            inn="1234567890"
        )

    def tearDown(self):
        # Закрываем сессию и удаляем таблицы
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_supplier_success(self):
        supplier = self.controller.create_supplier(
            comp_name="Новая компания",
            address="Новый адрес",
            phone="+79876543210",
            inn="0987654321"
        )
        self.assertIsNotNone(supplier.id)
        self.assertEqual(supplier.CompName, "Новая компания")

    def test_create_supplier_invalid_phone(self):
        with self.assertRaises(ValueError):
            self.controller.create_supplier(
                comp_name="Компания",
                address="Адрес",
                phone="неверный_номер",
                inn="1234567890"
            )

    def test_create_supplier_invalid_inn(self):
        with self.assertRaises(ValueError):
            self.controller.create_supplier(
                comp_name="Компания",
                address="Адрес",
                phone="+71234567890",
                inn="неверный_инн"
            )

    def test_get_supplier_by_id(self):
        found = self.controller.get_supplier_by_id(self.supplier.id)
        self.assertEqual(found.CompName, "Тестовая компания")

    def test_get_nonexistent_supplier(self):
        result = self.controller.get_supplier_by_id(999)
        self.assertIsNone(result)

    def test_update_supplier(self):
        updated = self.controller.update_supplier(
            self.supplier.id,
            CompName="Обновленное название",
            Number="+79999999999"
        )
        self.assertEqual(updated.CompName, "Обновленное название")
        self.assertEqual(updated.Number, "+79999999999")

    def test_update_supplier_with_invalid_data(self):
        with self.assertRaises(ValueError):
            self.controller.update_supplier(
                self.supplier.id,
                Number="invalid"
            )

    def test_delete_supplier(self):
        result = self.controller.delete_supplier(self.supplier.id)
        self.assertTrue(result)

        # Попытка удаления несуществующего поставщика
        result = self.controller.delete_supplier(999)
        self.assertFalse(result)

    def test_search_suppliers(self):
        # Создаем дополнительного поставщика для проверки поиска
        self.controller.create_supplier(
            comp_name="Фармацея",
            address="Москва",
            phone="+70000000000",
            inn="1111111111"
        )

        results = self.controller.search_suppliers("фарма")
        suppiles = self.controller.get_all_suppliers()
        # Ожидаем, что будет найден поставщик с 'Фармацея'
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].CompName, "Фармацея")

    def test_get_all_suppliers_filtering(self):
        suppliers = self.controller.get_all_suppliers(inn="1234567890")
        # Так как перед каждым тестом создается только один поставщик с указанным INN,
        # ожидаем, что будет найден ровно один.
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].INN, "1234567890")

    def test_supplier_medicines_relationship(self):
        # Добавляем лекарство для поставщика
        medicine = Medicine(
            MName="Тестовое лекарство",
            Price=100.0,
            Description="Описание",
            Category="Тест",
            BBT="2025-01-01",
            Supplier=self.supplier.id
        )
        self.session.add(medicine)
        self.session.commit()

        medicines = self.controller.get_supplier_medicines(self.supplier.id)
        self.assertEqual(len(medicines), 1)
        self.assertEqual(medicines[0].MName, "Тестовое лекарство")

    def test_supplier_stats(self):
        stats = self.controller.get_supplier_stats()
        # Изначально в базе один поставщик
        self.assertEqual(stats['total_suppliers'], 1)
        self.assertEqual(stats['suppliers_with_medicines'], 0)

        # Добавляем поставщика с лекарством
        supplier_with_med = self.controller.create_supplier(
            comp_name="С лекарствами",
            address="Адрес",
            phone="+71111111111",
            inn="2222222222"
        )
        medicine = Medicine(
            MName="Лекарство",
            Supplier=supplier_with_med.id,
            Price=200.0,
            Description="...",
            Category="...",
            BBT="2025-01-01"
        )
        self.session.add(medicine)
        self.session.commit()

        stats = self.controller.get_supplier_stats()
        self.assertEqual(stats['total_suppliers'], 2)
        self.assertEqual(stats['suppliers_with_medicines'], 1)

    def test_transaction_rollback(self):
        initial_count = self.controller.get_supplier_stats()['total_suppliers']

        try:
            self.controller.create_supplier(
                comp_name="Невалидный",
                address="Адрес",
                phone="invalid",
                inn="1234567890"
            )
        except ValueError:
            pass

        new_count = self.controller.get_supplier_stats()['total_suppliers']
        self.assertEqual(initial_count, new_count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
