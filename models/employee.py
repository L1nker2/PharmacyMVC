from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import date
from .base import Base

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    FName = Column(String(50), nullable=False)
    LName = Column(String(50), nullable=False)
    Number = Column(String(20), nullable=False)
    Position = Column(String(50), nullable=False)
    Login = Column(String(50), nullable=False)
    Pass = Column(String(255), nullable=False)
    DTB = Column(Date, nullable=False)
    Admin = Column(Boolean, nullable=False)

    # Связи: один сотрудник -> много заказов и много поставок
    orders = relationship('Order', back_populates='employee')
    shipments = relationship('Shipment', back_populates='employee')

    def get_experience(self):
        """Вычислить стаж (количество полных лет с даты найма, хранящейся в DTB)."""
        today = date.today()
        experience = today.year - self.DTB.year
        # Корректируем, если день рождения (годовщина найма) еще не наступил в этом году
        if (today.month, today.day) < (self.DTB.month, self.DTB.day):
            experience -= 1
        return experience

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)
