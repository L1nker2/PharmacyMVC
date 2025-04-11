from sqlalchemy.orm import Session, load_only
from typing import Optional, List, Type
from models.shipment import Shipment
from models.shipment_item import ShipmentItem


class ShipmentController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_shipment(self, shipment_data: dict, items: List[dict]) -> Shipment:
        """
        Создает новую поставку и связанные записи ShipmentItem.
        shipment_data – данные для Shipment (например, supplier_id, date и др.).
        items – список словарей с ключами 'medication_id' и 'quantity' для каждого медикамента в поставке.
        """
        # Создаем объект Shipment
        shipment = Shipment(**shipment_data)
        self.db.add(shipment)
        # Выполняем flush, чтобы сгенерировать shipment.id до создания связанных ShipmentItem&#8203;:contentReference[oaicite:5]{index=5}
        self.db.flush()
        # Создаем объекты ShipmentItem для каждого элемента поставки
        shipment_items = []
        for item in items:
            med_id = item.get("medication_id")
            qty = item.get("quantity", 0)
            shipment_item = ShipmentItem(Shipment=shipment.id, Medicine=med_id, Quantity=qty)
            shipment_items.append(shipment_item)
            self.db.add(shipment_item)
        # Фиксируем изменения в базе (создание и shipment, и shipment_items)
        self.db.commit()
        # Опционально можно обновить объект shipment, чтобы загрузить связанные элементы
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