import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.employee import Employee
from models.shipment import Shipment
from models.medicine import Medicine
from models.order import Order
from models.shipment_item import ShipmentItem
from models.supplier import Supplier

@pytest.fixture(scope="function")
def session():
    """Создает новую in-memory БД и сессию для каждого теста."""
    # Инициализируем SQLite в памяти
    engine = create_engine("sqlite:///:memory:")
    # Создаем все таблицы на основе моделей
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        yield db_session  # Передаем сессию в тест
    finally:
        db_session.close()
        Base.metadata.drop_all(engine)  # Удаляем схемы после теста для чистоты
        engine.dispose()
