from sqlalchemy import Column, Integer, Date, Numeric, String, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True)
    DateReg = Column(Date, nullable=False)
    Amount = Column(Numeric(10, 2), nullable=False)
    Status = Column(String(20), nullable=False)
    Client = Column(Integer, ForeignKey('clients.id'))
    Employee = Column(Integer, ForeignKey('employees.id'))
    Medicine = Column(Integer, ForeignKey('medicines.id'))

    # Связи
    client = relationship('Client', back_populates='orders')
    employee = relationship('Employee', back_populates='orders')
    medicine = relationship('Medicine', back_populates='orders')