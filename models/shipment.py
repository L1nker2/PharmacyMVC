from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean
from .base import Base
from sqlalchemy.orm import relationship

class Shipment(Base):
    __tablename__ = 'shipments'
    id = Column(Integer, primary_key=True)
    DateReg = Column(Date, nullable=False)
    Price = Column(Integer, nullable=False)
    Status = Column(Boolean, nullable=False)
    Supplier = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    Employee = Column(Integer, ForeignKey('employees.id'), nullable=False)

    # Связи: одна поставка -> один поставщик, один сотрудник; одна поставка -> много позиций (медикаментов)
    supplier = relationship('Supplier', back_populates='shipments')
    employee = relationship('Employee', back_populates='shipments')
    items = relationship('ShipmentItem', back_populates='shipment', cascade="all, delete-orphan")

    def get_total_quantity(self):
        """Вычислить общее количество всех медикаментов в данной поставке."""
        return sum(item.Quantity for item in self.items)

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)
