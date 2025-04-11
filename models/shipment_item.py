from sqlalchemy import Column, Integer, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class ShipmentItem(Base):
    __tablename__ = 'shipmentitem'
    id = Column(Integer, primary_key=True)
    Shipment = Column(Integer, ForeignKey('shipments.id'))
    Medicine = Column(Integer, ForeignKey('medicines.id'))
    Quantity = Column(Integer, nullable=False)

    # Связи: одна позиция принадлежит одной поставке и одному медикаменту
    shipment = relationship('Shipment', back_populates='items')
    medicine = relationship('Medicine', back_populates='shipmentitems')

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)
