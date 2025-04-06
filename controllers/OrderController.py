from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from typing import List, Optional, Dict
from models.order import Order


class OrderController:
    def __init__(self, session: Session):
        self.session = session

    def create_order(self,
                     date_reg: date,
                     amount: float,
                     status: str,
                     client_id: int,
                     employee_id: int) -> 'Order':
        """
        Создание нового заказа
        """
        try:
            order = Order(
                DateReg=date_reg,
                Amount=amount,
                Status=status,
                Client=client_id,
                Employee=employee_id
            )
            self.session.add(order)
            self.session.commit()
            return order
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка создания заказа: {str(e)}")

    def get_order_by_id(self,
                        order_id: int,
                        include_relations: bool = False) -> Optional['Order']:
        """
        Получение заказа по ID
        """
        try:
            query = self.session.query(Order)
            if include_relations:
                query = query.options(
                    joinedload(Order.client),
                    joinedload(Order.employee)
                )
            return query.get(order_id)
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения заказа: {str(e)}")

    def update_order(self,
                     order_id: int,
                     **kwargs) -> 'Order':
        """
        Обновление данных заказа
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                raise ValueError("Заказ не найден")

            valid_fields = {'DateReg', 'Amount', 'Status', 'Client', 'Employee'}
            for key, value in kwargs.items():
                if key in valid_fields:
                    setattr(order, key, value)

            self.session.commit()
            return order
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка обновления заказа: {str(e)}")

    def delete_order(self, order_id: int) -> bool:
        """
        Удаление заказа
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return False

            self.session.delete(order)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка удаления заказа: {str(e)}")

    def get_all_orders(self,
                       client_id: Optional[int] = None,
                       employee_id: Optional[int] = None,
                       status: Optional[str] = None,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> List['Order']:
        """
        Получение списка заказов с фильтрами
        """
        try:
            query = self.session.query(Order)

            if client_id:
                query = query.filter(Order.Client == client_id)
            if employee_id:
                query = query.filter(Order.Employee == employee_id)
            if status:
                query = query.filter(Order.Status == status)
            if start_date:
                query = query.filter(Order.DateReg >= start_date)
            if end_date:
                query = query.filter(Order.DateReg <= end_date)

            return query.all()
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения списка заказов: {str(e)}")

    def get_orders_by_status(self, status: str) -> List['Order']:
        """
        Получение заказов по статусу
        """
        return self.get_all_orders(status=status)

    def get_orders_in_date_range(self,
                                 start_date: date,
                                 end_date: date) -> List['Order']:
        """
        Получение заказов в диапазоне дат
        """
        return self.get_all_orders(start_date=start_date, end_date=end_date)

    def update_order_status(self,
                            order_id: int,
                            new_status: str) -> 'Order':
        """
        Обновление статуса заказа
        """
        return self.update_order(order_id, Status=new_status)

    def get_order_statistics(self) -> Dict[str, float]:
        """
        Получение статистики по заказам
        """
        try:
            result = {
                'total_orders': 0,
                'total_amount': 0.0,
                'average_order': 0.0
            }

            # Общее количество заказов
            total = self.session.query(Order).count()
            result['total_orders'] = total

            # Сумма всех заказов
            amount_sum = self.session.query(
                func.sum(Order.Amount)
            ).scalar() or 0.0
            result['total_amount'] = float(amount_sum)

            # Средний чек
            if total > 0:
                result['average_order'] = float(amount_sum) / total

            return result
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения статистики: {str(e)}")