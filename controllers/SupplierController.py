import sqlalchemy
from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.supplier import Supplier


class SupplierController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_supplier(self, supplier_data: dict) -> Supplier:
        """Создает нового поставщика."""
        if not self.is_name_unique(supplier_data['CompName']):
            raise sqlalchemy.exc.IntegrityError(statement="UNIQUE constraint failed", params="UNIQUE constraint failed",
                                                orig="UNIQUE constraint failed")
        if supplier_data['CompName'] == "" or supplier_data['Address'] == ""\
            or supplier_data['Number'] == "" or supplier_data['INN'] == "":
            raise ValueError("Fill in all fields")
        supplier = Supplier(**supplier_data)
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def get_supplier_by_id(self, supplier_id: int) -> Type[Supplier]:
        """Возвращает поставщика по ID или None, если не найден."""
        supplier = self.db.get(Supplier, supplier_id)
        if supplier is None:
            raise ValueError("Supplier with ID {} not found".format(supplier_id))
        else: return supplier

    def update_supplier(self, supplier_id: int, update_data: dict) -> Type[Supplier] | None:
        """Обновляет данные поставщика по ID. Возвращает обновленный объект или None."""
        supplier = self.db.get(Supplier, supplier_id)
        if update_data['CompName'] == "" or update_data['Address'] == ""\
            or update_data['Number'] == "" or update_data['INN'] == "":
            raise ValueError("Fill in all fields")
        if not supplier:
            raise ValueError("Supplier with ID {} not found".format(supplier_id))
        for field, value in update_data.items():
            setattr(supplier, field, value)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def delete_supplier(self, supplier_id: int) -> Type[Supplier] | None:
        """Удаляет поставщика по ID. Возвращает удалённый объект или None."""
        supplier = self.db.get(Supplier, supplier_id)
        if not supplier:
            raise ValueError("Supplier with ID {} not found".format(supplier_id))
        self.db.delete(supplier)
        self.db.commit()
        return supplier

    def get_all(self) -> list[Type[Supplier]]:
        """Возвращает список всех поставщиков (с ограниченным набором полей)."""
        return self.db.query(Supplier).options(
            load_only(Supplier.id, Supplier.CompName)
        ).all()

    def is_name_unique(self, name: str) -> bool:
        """Проверяет, уникален ли указанный CompName (True, если такого CompName нет в базе)."""
        existing = self.db.query(Supplier).filter(Supplier.CompName == name).first()
        return existing is None