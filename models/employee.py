from sqlalchemy import Column, Integer, String, Date
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

    # Исправлено: back_populates='employee'
    orders = relationship('Order', back_populates='employee')

    def get_experience(self):
        today = date.today()
        experience = today.year - self.DTB.year
        if (today.month, today.day) < (self.DTB.month, self.DTB.day):
            experience -= 1
        return experience