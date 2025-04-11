import pytest
import sqlalchemy
from controllers.ShipmentItemController import ShipmentItemController
from controllers.ShipmentController import ShipmentController
from controllers.OrderController import OrderController
from controllers.SupplierController import SupplierController
from controllers.MedicineController import MedicineController
from models.shipment_item import ShipmentItem

def setup_shipment_and_medicine(session):
    """Вспомогательная функция для подготовки связанных Shipment и Medicine."""
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    shipment_ctrl = ShipmentController(session)
    medicine_ctrl = MedicineController(session)
    # Создаем необходимые объекты: Supplier -> Order -> Shipment, и Medicine
    supplier = supplier_ctrl.create(name="SupplierForItem", contact="123")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-12-01")
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-12-02")
    medicine = medicine_ctrl.create(name="ItemMed", price=20.0)
    return shipment, medicine

def test_create_shipment_item_success(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    item = item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=100)
    assert item.id is not None
    # Проверяем через ORM, что элемент сохранен
    item_db = session.query(ShipmentItem).get(item.id)
    assert item_db.shipment_id == shipment.id
    assert item_db.medicine_id == medicine.id
    assert item_db.quantity == 100

def test_get_shipment_item_by_id(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    item = item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=5)
    fetched = item_ctrl.get_by_id(item.id)
    assert fetched.medicine_id == medicine.id
    assert fetched.quantity == 5

def test_get_shipment_item_not_found(session):
    item_ctrl = ShipmentItemController(session)
    with pytest.raises(Exception):
        item_ctrl.get_by_id(99999)

def test_create_shipment_item_missing_data(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    # Попытка создания без medicine_id
    with pytest.raises(ValueError):
        item_ctrl.create(shipment_id=shipment.id, medicine_id=None, quantity=10)

def test_create_shipment_item_invalid_shipment(session):
    # Создаем только Medicine, а Shipment не создаем
    medicine_ctrl = MedicineController(session)
    medicine = medicine_ctrl.create(name="MedOnly", price=5.0)
    item_ctrl = ShipmentItemController(session)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        item_ctrl.create(shipment_id=99999, medicine_id=medicine.id, quantity=1)

def test_create_shipment_item_invalid_medicine(session):
    # Создаем Shipment, а Medicine не создаем
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    shipment_ctrl = ShipmentController(session)
    supplier = supplier_ctrl.create(name="NoMedSup", contact="321")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-08-08")
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-08-09")
    item_ctrl = ShipmentItemController(session)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        item_ctrl.create(shipment_id=shipment.id, medicine_id=99999, quantity=1)

def test_create_shipment_item_invalid_quantity(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    # Нулевое количество недопустимо
    with pytest.raises(ValueError):
        item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=0)

def test_update_shipment_item_success(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    item = item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=2)
    # Обновляем количество
    updated = item_ctrl.update(item.id, quantity=3)
    assert updated.quantity == 3
    item_db = session.query(ShipmentItem).get(item.id)
    assert item_db.quantity == 3

def test_update_shipment_item_not_found(session):
    item_ctrl = ShipmentItemController(session)
    with pytest.raises(Exception):
        item_ctrl.update(123456, quantity=10)

def test_update_shipment_item_invalid_data(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    item = item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=10)
    # Попытка обновить на недопустимое значение (например, 0)
    with pytest.raises(ValueError):
        item_ctrl.update(item.id, quantity=0)
    # Попытка обновить на несуществующую medicine_id
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        item_ctrl.update(item.id, medicine_id=99999)

def test_delete_shipment_item_success(session):
    shipment, medicine = setup_shipment_and_medicine(session)
    item_ctrl = ShipmentItemController(session)
    item = item_ctrl.create(shipment_id=shipment.id, medicine_id=medicine.id, quantity=50)
    item_ctrl.delete(item.id)
    assert session.query(ShipmentItem).get(item.id) is None

def test_delete_shipment_item_not_found(session):
    item_ctrl = ShipmentItemController(session)
    with pytest.raises(Exception):
        item_ctrl.delete(55555)
