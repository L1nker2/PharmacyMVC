from sqlalchemy.orm import Session, load_only
from typing import Optional, List, Type
from models.medicine import Medicine
from models.shipment import Shipment
from models.employee import Employee
from models.supplier import Supplier
from models.shipment_item import ShipmentItem


class ShipmentController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_suppliers(self):
        """Получение всех поставщиков для выпадающего списка"""
        return self.db.query(Supplier).order_by(Supplier.CompName).all()

    def get_all_employees(self):
        """Получение всех сотрудников для выпадающего списка"""
        return self.db.query(Employee).order_by(Employee.LName).all()

    def create_shipment(self, shipment_data: dict, items: List[dict]) -> Shipment:
        """
        Создает новую поставку и связанные записи ShipmentItem.
        shipment_data – данные для Shipment (например, supplier_id, date и др.).
        items – список словарей с ключами 'medication_id' и 'quantity' для каждого медикамента в поставке.
        Автоматически рассчитывает общую стоимость поставки на основе цен медикаментов.
        """
        # Рассчитываем общую стоимость поставки
        total_price = 0
        for item in items:
            med_id = item.get("medication_id")
            qty = item.get("quantity", 0)
            # Получаем медикамент из базы данных
            medication = self.db.query(Medicine).filter(Medicine.id == med_id).first()
            if not medication:
                raise ValueError(f"Медикамент с ID {med_id} не найден")
            total_price += medication.Price * qty

        # Обновляем цену в shipment_data (перезаписываем, если была передана)
        shipment_data["Price"] = total_price

        # Создаем объект Shipment
        shipment = Shipment(**shipment_data)
        self.db.add(shipment)
        self.db.flush()

        # Создаем объекты ShipmentItem для каждого элемента поставки
        shipment_items = []
        for item in items:
            med_id = item.get("medication_id")
            qty = item.get("quantity", 0)
            shipment_item = ShipmentItem(Shipment=shipment.id, Medicine=med_id, Quantity=qty)
            shipment_items.append(shipment_item)
            self.db.add(shipment_item)

        # Обновляем количество медикаментов на складе
        for item in items:
            med_id = item.get("medication_id")
            qty = item.get("quantity", 0)
            medication = self.db.query(Medicine).filter(Medicine.id == med_id).first()
            medication.Count += qty

        # Фиксируем все изменения в базе
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

    def get_shipment_by_id(self, shipment_id: int) -> Optional[Shipment]:
        """Возвращает поставку по ID или None, если не найдена."""
        return self.db.get(Shipment, shipment_id)

    def update_shipment(self, shipment_id: int, update_data: dict) -> Type[Shipment] | None:
        """Обновляет данные поставки по ID. Возвращает обновленный объект или None."""
        shipment = self.db.get(Shipment, shipment_id)
        if not shipment:
            return None
        for field, value in update_data.items():
            setattr(shipment, field, value)
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

    def delete_shipment(self, shipment_id: int) -> Type[Shipment] | None:
        """Удаляет поставку по ID. Возвращает удалённый объект или None."""
        shipment = self.db.get(Shipment, shipment_id)
        if not shipment:
            return None
        shipment_items = self.db.query(ShipmentItem).filter(ShipmentItem.Shipment == shipment.id).all()
        for shipment_item in shipment_items:
            self.db.delete(shipment_item)
        self.db.delete(shipment)
        self.db.commit()
        return shipment

    def get_all(self) -> list[Type[Shipment]]:
        """Возвращает список всех поставок (с ограниченным набором полей)."""
        return self.db.query(Shipment).options(
            load_only(Shipment.id, Shipment.Supplier, Shipment.DateReg)
        ).all()