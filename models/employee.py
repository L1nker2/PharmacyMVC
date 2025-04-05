from sqlalchemy import Column, Integer, String, Date
from datetime import date
from .base import Base

class Employee(Base):
    """
    Модель сотрудника аптеки.
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор сотрудника")
    FName = Column(String(50), nullable=False, doc="Имя сотрудника")
    LName = Column(String(50), nullable=False, doc="Фамилия сотрудника")
    Number = Column(String(20), nullable=False, doc="Контактный телефон")
    Position = Column(String(50), nullable=False, doc="Должность")
    Login = Column(String(50), nullable=False, doc="Логин для входа")
    Pass = Column(String(255), nullable=False, doc="Хэш пароля")
    DTB = Column(Date, nullable=False, doc="Дата трудоустройства (ГГГГ-ММ-ДД)")

    def get_experience(self):
        today = date.today()
        experience = today.year - self.DTB.year
        if (today.month, today.day) < (self.DTB.month, self.DTB.day):
            experience -= 1
        return experience