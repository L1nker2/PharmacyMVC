from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.medicine import Medicine
from models.order import Order


class OrderController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_order(self, order_data: dict) -> Order:
        """Создает новый заказ и уменьшает количество медикамента на складе."""
        # Проверка заполненности полей
        required_fields = ['DateReg', 'Amount', 'Status', 'Employee', 'Medicine']
        if any(not order_data.get(field) for field in required_fields):
            raise ValueError("Все обязательные поля должны быть заполнены")

        if self.db.in_transaction():
            self.db.commit()

        # Начинаем транзакцию
        self.db.begin()

        # Получаем медикамент и блокируем запись для обновления
        medicine = self.db.query(Medicine).filter_by(id=order_data['Medicine']).with_for_update().first()
        if not medicine:
            raise ValueError("Медикамент не найден")

        # Проверяем достаточное количество
        if medicine.Count < order_data['Amount']:
            raise ValueError(f"Недостаточно медикамента на складе. Доступно: {medicine.Count}")

        # Уменьшаем количество медикамента
        medicine.Count -= order_data['Amount']

        # Создаем заказ
        order = Order(**order_data)
        self.db.add(order)

        # Сохраняем изменения
        self.db.commit()
        self.db.refresh(order)
        self.db.refresh(medicine)

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
