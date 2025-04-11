from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean
from .base import Base
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    DateReg = Column(Date, nullable=False)
    Amount = Column(Integer, nullable=False)
    Status = Column(Boolean, nullable=False)
    Employee = Column(Integer, ForeignKey('employees.id'), nullable=False)
    Medicine = Column(Integer, ForeignKey('medicines.id'), nullable=False)

    # Связи: один заказ -> один сотрудник (автор) и один медикамент
    employee = relationship('Employee', back_populates='orders')
    medicine = relationship('Medicine', back_populates='orders')

    def get_total_cost(self):
        """Рассчитать общую стоимость заказа (Price * Amount связанного медикамента)."""
        return self.medicine.Price * self.Amount if self.medicine else None

    def __iter__(self):
        for column in self.__table__.columns:
            yield getattr(self, column.name)
