from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Medicine(Base):
    """
    Модель лекарственного препарата.
    """
    __tablename__ = 'medicines'

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор препарата")
    MName = Column(String(50), nullable=False, doc="Название лекарства")
    Price = Column(Numeric(10, 2), nullable=False, doc="Цена за единицу")
    Description = Column(String(255), nullable=False, doc="Описание препарата")
    Category = Column(String(50), nullable=False, doc="Категория лекарства")
    BBT = Column(String(50), nullable=False, doc="Срок годности")
    Supplier = Column(Integer, ForeignKey('suppliers.id'), nullable=False, doc="ID поставщика")

    # Связи с таблицами
    supplier_rel = relationship("Supplier", back_populates="medicines")
    orders = relationship('Order', back_populates='medicine')
