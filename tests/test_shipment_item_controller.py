import pytest
from sqlalchemy import inspect
from models.shipment_item import ShipmentItem
from models.shipment import Shipment
from models.medicine import Medicine
from models.supplier import Supplier
from models.employee import Employee
from controllers.ShipmentItemController import ShipmentItemController
from datetime import date, datetime


@pytest.fixture
def item_controller(session):
    return ShipmentItemController(session)


@pytest.fixture
def setup_data(session):
    # Создаем связанные сущности
    supplier = Supplier(id=1, CompName="Test Supplier", Address="Test Address",
                        Number="Test Number", INN="Test INN")
    employee = Employee(id=1, FName="Test FName",
                        LName="Test LName", Number="Test Number",
                        Position="Test Position", Login="Test Login",
                        Pass="Test Pass",
                        DTB=datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin=False)
    medicine = Medicine(id=1, MName="Test Medicine",
                        Price=100, Count=100,
                        Description="Test Description",
                        Category="Test Category", BT="Test BT",
                        Supplier=1)
    medicine2 = Medicine(id=2, MName="Test Medicine2",
                        Price=100, Count=100,
                        Description="Test Description",
                        Category="Test Category", BT="Test BT",
                        Supplier=1)
    shipment = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date.today(),
        Amount=100,
        Status=True
    )

    session.add_all([supplier, employee, medicine, shipment])
    session.commit()
    return {
        "shipment_id": shipment.id,
        "medicine_id": medicine.id,
        "medicine2_id": medicine2.id
    }


def test_create_shipmentitem(item_controller, session, setup_data):
    # Тестовые данные
    item_data = {
        "Shipment": setup_data["shipment_id"],
        "Medicine": setup_data["medicine_id"],
        "Quantity": 10
    }

    # Создаем запись
    created_item = item_controller.create_shipmentitem(item_data)

    # Проверяем базовые атрибуты
    assert created_item is not None
    assert created_item.Shipment == setup_data["shipment_id"]
    assert created_item.Medicine == setup_data["medicine_id"]
    assert created_item.Quantity == 10

    # Проверяем запись в БД
    db_item = session.get(ShipmentItem, created_item.Shipment)
    assert db_item is not None


def test_get_shipmentitem_by_id(item_controller, session, setup_data):
    # Создаем тестовый объект
    item = ShipmentItem(
        Shipment=setup_data["shipment_id"],
        Medicine=setup_data["medicine_id"],
        Quantity=15
    )
    session.add(item)
    session.commit()

    # Получаем существующий объект
    result = item_controller.get_shipmentitem_by_id(item.Shipment)
    assert result is not None
    assert result.Quantity == 15

    # Проверяем несуществующий ID
    assert item_controller.get_shipmentitem_by_id(999) is None


def test_update_shipmentitem(item_controller, session, setup_data):
    # Создаем тестовый объект
    item = ShipmentItem(
        Shipment=setup_data["shipment_id"],
        Medicine=setup_data["medicine_id"],
        Quantity=20
    )
    session.add(item)
    session.commit()

    # Обновляем данные
    update_data = {"Quantity": 25}
    updated = item_controller.update_shipmentitem(
        item.Shipment,
        update_data
    )

    # Проверяем обновление
    assert updated.Quantity == 25
    db_item = session.get(ShipmentItem, item.Shipment)
    assert db_item.Quantity == 25

    # Проверяем несуществующий ID
    assert item_controller.update_shipmentitem(999, {"Quantity": 10}) is None


def test_delete_shipmentitem(item_controller, session, setup_data):
    # Создаем тестовый объект
    item = ShipmentItem(
        Shipment=setup_data["shipment_id"],
        Medicine=setup_data["medicine_id"],
        Quantity=30
    )
    session.add(item)
    session.commit()

    # Удаляем объект
    deleted = item_controller.delete_shipmentitem(item.Shipment)
    assert deleted is not None

    # Проверяем удаление
    assert session.get(ShipmentItem, item.Shipment) is None

    # Проверяем несуществующий ID
    assert item_controller.delete_shipmentitem(999) is None


def test_get_all_shipmentitems(item_controller, session, setup_data):
    # Создаем несколько записей с разными Medicine
    items = [
        ShipmentItem(
            Shipment=setup_data["shipment_id"],
            Medicine=setup_data["medicine_id"],
            Quantity=5
        ),
        ShipmentItem(
            Shipment=setup_data["shipment_id"],
            Medicine=setup_data["medicine2_id"],  # Используем второе лекарство
            Quantity=10
        )
    ]
    session.add_all(items)
    session.commit()

    # Остальная часть теста
    result = item_controller.get_all()
    assert len(result) == 2

    # Проверяем загрузку только нужных полей
    for item in result:
        insp = inspect(item)
        unloaded = insp.unloaded

        # Проверяем загруженные поля
        assert "id" not in unloaded
        assert "Shipment" not in unloaded
        assert "Medicine" not in unloaded
        assert "Quantity" not in unloaded

        # Проверяем НЕзагруженные поля (если есть другие атрибуты в модели)
        # Например, если есть relationship-поля:
        if hasattr(ShipmentItem, 'shipment'):
            assert "shipment" in unloaded  # relationship name, not column
        if hasattr(ShipmentItem, 'medicine'):
            assert "medicine" in unloaded

    # Проверяем содержимое
    quantities = {item.Quantity for item in result}
    assert 5 in quantities
    assert 10 in quantities