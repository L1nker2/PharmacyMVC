from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Дополнительно можно добавить общие методы для всех моделей
class BaseModel:
    def __init__(self):
        self.__table__ = None
        self.id = None

    def __repr__(self):
        """Универсальный __repr__ для всех моделей"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self):
        """Конвертация объекта в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Объединяем базовый класс с общими методами
Base = declarative_base(cls=BaseModel)
engine = create_engine("mysql+mysqldb://python:python@127.0.0.1/apteka",
    pool_recycle=3600,
    echo=True)