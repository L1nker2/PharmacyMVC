from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.shipment_item import ShipmentItem

class ShipmentItemController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_shipmentitem(self, item_data: dict) -> ShipmentItem:
        """Создает новую запись ShipmentItem."""
        shipment_item = ShipmentItem(**item_data)
        self.db.add(shipment_item)
        self.db.commit()
        self.db.refresh(shipment_item)
        return shipment_item

    def get_shipmentitem_by_id(self, item_id: int) -> Optional[ShipmentItem]:
        """Возвращает ShipmentItem по ID или None, если не найден."""
        return self.db.get(ShipmentItem, item_id)

    def update_shipmentitem(self, item_id: int, update_data: dict) -> Type[ShipmentItem] | None:
        """Обновляет данные ShipmentItem по ID. Возвращает обновленный объект или None."""
        shipment_item = self.db.get(ShipmentItem, item_id)
        if not shipment_item:
            return None
        for field, value in update_data.items():
            setattr(shipment_item, field, value)
        self.db.commit()
        self.db.refresh(shipment_item)
        return shipment_item

    def delete_shipmentitem(self, item_id: int) -> Type[ShipmentItem] | None:
        """Удаляет ShipmentItem по ID. Возвращает удалённый объект или None."""
        shipment_item = self.db.get(ShipmentItem, item_id)
        if not shipment_item:
            return None
        self.db.delete(shipment_item)
        self.db.commit()
        return shipment_item

    def get_all(self) -> list[Type[ShipmentItem]]:
        """Возвращает список всех ShipmentItem (с ограниченным набором полей)."""
        return self.db.query(ShipmentItem).options(
            load_only(ShipmentItem.id, ShipmentItem.Shipment, ShipmentItem.Medicine, ShipmentItem.Quantity)
        ).all()