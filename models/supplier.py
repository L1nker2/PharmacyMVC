from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    CompName = Column(String(100), nullable=False)
    Address = Column(String(100), nullable=False)
    Number = Column(String(20), nullable=False)
    INN = Column(String(20), nullable=False)

    # Связи: один поставщик -> много поставок и много медикаментов
    shipments = relationship('Shipment', back_populates='supplier')
    medicines = relationship('Medicine', back_populates='supplier')

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)
