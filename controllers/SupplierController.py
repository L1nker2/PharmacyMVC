from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import List, Optional, Dict
from models.supplier import Supplier
from models.medicine import Medicine


class SupplierController:
    def __init__(self, session: Session):
        self.session = session

    def create_supplier(self,
                        comp_name: str,
                        address: str,
                        phone: str,
                        inn: str) -> 'Supplier':
        """
        Создание нового поставщика
        """
        try:
            # Валидация данных
            self._validate_phone(phone)
            self._validate_inn(inn)

            supplier = Supplier(
                CompName=comp_name,
                Adress=address,
                Number=phone,
                INN=inn
            )
            self.session.add(supplier)
            self.session.commit()
            return supplier
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка создания поставщика: {str(e)}")

    def get_supplier_by_id(self,
                           supplier_id: int,
                           include_medicines: bool = False) -> Optional['Supplier']:
        """
        Получение поставщика по ID
        """
        try:
            query = self.session.query(Supplier)
            if include_medicines:
                query = query.options(joinedload(Supplier.medicines))
            return query.get(supplier_id)
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения поставщика: {str(e)}")

    def update_supplier(self,
                        supplier_id: int,
                        **kwargs) -> 'Supplier':
        """
        Обновление данных поставщика
        """
        try:
            supplier = self.get_supplier_by_id(supplier_id)
            if not supplier:
                raise ValueError("Поставщик не найден")

            # Валидация обновляемых полей
            if 'Number' in kwargs:
                self._validate_phone(kwargs['Number'])
            if 'INN' in kwargs:
                self._validate_inn(kwargs['INN'])

            valid_fields = {'CompName', 'Adress', 'Number', 'INN'}
            for key, value in kwargs.items():
                if key in valid_fields:
                    setattr(supplier, key, value)

            self.session.commit()
            return supplier
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка обновления поставщика: {str(e)}")

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        Удаление поставщика
        """
        try:
            supplier = self.get_supplier_by_id(supplier_id)
            if not supplier:
                return False

            self.session.delete(supplier)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка удаления поставщика: {str(e)}")

    def get_all_suppliers(self,
                          search_query: Optional[str] = None,
                          inn: Optional[str] = None) -> List['Supplier']:
        """
        Получение списка поставщиков с фильтрами
        """
        try:
            query = self.session.query(Supplier)

            if search_query:
                query = query.filter(
                    Supplier.CompName.ilike(f"%{search_query}%") |
                    Supplier.Adress.ilike(f"%{search_query}%")
                )
            if inn:
                query = query.filter(Supplier.INN == inn)

            return query.order_by(Supplier.CompName).all()
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения списка поставщиков: {str(e)}")

    def search_suppliers(self, search_term: str) -> List['Supplier']:
        """
        Поиск поставщиков по названию компании или адресу через выполнение SQL запроса.
        """
        pattern = f"%{search_term}%"
        sql = text("""
            SELECT * FROM suppliers
            WHERE CompName LIKE :pattern OR Adress LIKE :pattern
            ORDER BY CompName
        """)
        try:
            result = self.session.execute(sql, {'pattern': pattern})
            # Получаем результаты как словари
            rows = result.mappings().all()
            # Преобразуем каждую строку в объект Supplier
            suppliers = [Supplier(**row) for row in rows]
            return suppliers
        except Exception as e:
            raise ValueError(f"Ошибка выполнения запроса поиска поставщиков: {str(e)}")

    def _validate_phone(self, phone: str):
        """
        Базовая валидация номера телефона
        """
        if not phone.replace('+', '').replace(' ', '').isdigit():
            raise ValueError("Некорректный формат номера телефона")

    def _validate_inn(self, inn: str):
        """
        Базовая валидация ИНН
        """
        if not inn.isdigit():
            raise ValueError("ИНН должен содержать только цифры")
        if len(inn) not in (10, 12):
            raise ValueError("Некорректная длина ИНН")

    def get_supplier_medicines(self, supplier_id: int) -> List['Medicine']:
        """
        Получение списка лекарств поставщика
        """
        supplier = self.get_supplier_by_id(supplier_id, include_medicines=True)
        if not supplier:
            return []
        return supplier.medicines

    def get_supplier_stats(self) -> Dict[str, int]:
        """
        Статистика по поставщикам
        """
        try:
            total_suppliers = self.session.query(Supplier).count()
            suppliers_with_medicines = self.session.query(Supplier) \
                .filter(Supplier.medicines.any()).count()

            return {
                'total_suppliers': total_suppliers,
                'suppliers_with_medicines': suppliers_with_medicines,
                'suppliers_without_medicines': total_suppliers - suppliers_with_medicines
            }
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения статистики: {str(e)}")