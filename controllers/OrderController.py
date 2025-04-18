from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.order import Order


class OrderController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_order(self, order_data: dict) -> Order:
        """Создает новый заказ."""
        if order_data['DateReg'] == '' or order_data['Amount'] == ''\
            or order_data['Status'] == '' or order_data['Employee'] == ''\
            or order_data['Medicine'] == '':
            raise ValueError("Fill all fields")
        if order_data['DateReg'] is None or order_data['Amount'] is None\
            or order_data['Status'] is None or order_data['Employee'] is None\
            or order_data['Medicine'] is None:
            raise ValueError("Fill all fields")
        if order_data.__contains__(None) or order_data.__contains__(''):
            raise ValueError("Fill all fields")
        order = Order(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_by_id(self, order_id: int) -> Type[Order]:
        """Возвращает заказ по ID или None, если не найден."""
        order = self.db.get(Order, order_id)
        if order is None:
            raise ValueError("Order not found")
        else: return order

    def update_order(self, order_id: int, update_data: dict) -> Type[Order] | None:
        """Обновляет данные заказа по ID. Возвращает обновленный объект или None."""
        order = self.db.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        for field, value in update_data.items():
            setattr(order, field, value)
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, order_id: int) -> Type[Order] | None:
        """Удаляет заказ по ID. Возвращает удалённый объект или None."""
        order = self.db.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        self.db.delete(order)
        self.db.commit()
        return order

    def get_all(self) -> list[Type[Order]]:
        """Возвращает список всех заказов (с ограниченным набором полей)."""
        # Например, выбираем поля: id, количество и ссылку на медикамент (можно имя медикамента через join, если нужно)
        return self.db.query(Order).options(
            load_only(Order.id, Order.Amount, Order.Medicine)
        ).all()

    def get_total_cost(self, order_id: int) -> Optional[float]:
        """Вычисляет общую стоимость заказа (Price * Amount). Возвращает сумму или None, если заказ не найден."""
        order = self.db.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        # Предполагаем, что у заказа есть связанный объект medicine и поле amount (количество)
        medicine = order.Medicine  # может выполниться ленивой загрузкой Medicine, если не загружен
        amount = getattr(order, "amount", None)  # количество заказанного товара
        if medicine is None or amount is None:
            return None
        # Общая стоимость = цена медикамента * количество
        total = medicine.price * amount
        return total
