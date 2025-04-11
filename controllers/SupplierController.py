from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.supplier import Supplier


class SupplierController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_supplier(self, supplier_data: dict) -> Supplier:
        """Создает нового поставщика."""
        supplier = Supplier(**supplier_data)
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Возвращает поставщика по ID или None, если не найден."""
        return self.db.get(Supplier, supplier_id)

    def update_supplier(self, supplier_id: int, update_data: dict) -> Type[Supplier] | None:
        """Обновляет данные поставщика по ID. Возвращает обновленный объект или None."""
        supplier = self.db.get(Supplier, supplier_id)
        if not supplier:
            return None
        for field, value in update_data.items():
            setattr(supplier, field, value)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def delete_supplier(self, supplier_id: int) -> Type[Supplier] | None:
        """Удаляет поставщика по ID. Возвращает удалённый объект или None."""
        supplier = self.db.get(Supplier, supplier_id)
        if not supplier:
            return None
        self.db.delete(supplier)
        self.db.commit()
        return supplier

    def get_all(self) -> list[Type[Supplier]]:
        """Возвращает список всех поставщиков (с ограниченным набором полей)."""
        return self.db.query(Supplier).options(
            load_only(Supplier.id, Supplier.CompName)
        ).all()