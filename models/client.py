from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from .base import Base

class Client(Base):
    """
    Модель клиента аптеки.
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор клиента")
    FName = Column(String(50), nullable=False, doc="Имя клиента")
    LName = Column(String(50), nullable=False, doc="Фамилия клиента")
    Number = Column(String(20), nullable=False, doc="Контактный телефон")
    Login = Column(String(50), nullable=False, doc="Логин для входа")
    Pass = Column(String(255), nullable=False, doc="Хэш пароля")
    Balance = Column(Numeric(10, 2), nullable=False, doc="Баланс счета")

    Orders = relationship('Orders', secondary='Orders')

    # Можно переопределить метод to_dict для специфических нужд
    def to_dict(self):
        data = super().to_dict()
        data.pop('Pass', None)  # Исключаем пароль из сериализации
        return data