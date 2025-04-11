from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Medicine(Base):
    __tablename__ = 'medicines'
    id = Column(Integer, primary_key=True)
    MName = Column(String(100), nullable=False)
    Price = Column(Integer, nullable=False)
    Count = Column(Integer, nullable=False)
    Description = Column(String(255))
    Category = Column(String(50))
    BT = Column(String(50))
    Supplier = Column(Integer, ForeignKey('suppliers.id'))

    # Связи: многие медикаменты -> один поставщик; один медикамент -> много заказов; один медикамент -> много позиций в поставках
    supplier = relationship('Supplier', back_populates='medicines')
    orders = relationship('Order', back_populates='medicine')
    shipmentitems = relationship('ShipmentItem', back_populates='medicine')

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)

