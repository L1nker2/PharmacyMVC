# models/client.py
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from .base import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    FName = Column(String(50), nullable=False)
    LName = Column(String(50), nullable=False)
    Number = Column(String(20), nullable=False)
    Login = Column(String(50), nullable=False)
    Pass = Column(String(255), nullable=False)
    Balance = Column(Numeric(10, 2), nullable=False)

    orders = relationship('Order', back_populates='client')

    def to_dict(self):
        data = super().to_dict()
        data.pop('Pass', None)
        return data