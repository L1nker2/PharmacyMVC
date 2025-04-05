from sqlalchemy import Column, Integer, Date, Numeric, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    """
    Модель заказа в аптеке.
    """
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор заказа")
    DateReg = Column(Date, nullable=False, doc="Дата регистрации заказа")
    Amount = Column(Numeric(10, 2), nullable=False, doc="Сумма заказа")
    Status = Column(String(20), nullable=False, doc="Статус заказа")
    Client = Column(Integer, ForeignKey('client.id'), doc="Уникальный идентификатор клиента")
    Employee = Column(Integer, ForeignKey('employee.id'), doc="Уникальный идентификатор работника")
