from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Supplier(Base):
    """
    Модель поставщика лекарств.
    """
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, nullable=False, doc="Уникальный ID поставщика")
    CompName = Column(String(100), nullable=False, doc="Название компании")
    Adress = Column(String(255), nullable=False, doc="Юридический адрес")
    Number = Column(String(20), nullable=False, doc="Контактный телефон")
    INN = Column(String(50), nullable=False, doc="ИНН организации")
    medicines = relationship("Medicine", back_populates="supplier_rel")
