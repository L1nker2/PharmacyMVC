import pytest
import sqlalchemy
from controllers.ShipmentController import ShipmentController
from controllers.OrderController import  OrderController
from controllers.SupplierController import SupplierController
from models.shipment import Shipment

def test_create_shipment_success(session):
    # Создаем заказ, к которому будет относиться shipment
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="ShipSupplier", contact="555")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-11-11")

    shipment_ctrl = ShipmentController(session)
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-11-12")
    assert shipment.id is not None
    # Проверяем связь с заказом
    ship_db = session.query(Shipment).get(shipment.id)
    assert ship_db.order_id == order.id
    assert ship_db.shipped_date == "2025-11-12"

def test_get_shipment_by_id(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="ShipSupplier2", contact="666")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-10-10")

    shipment_ctrl = ShipmentController(session)
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-10-15")
    fetched = shipment_ctrl.get_by_id(shipment.id)
    assert fetched.order_id == order.id
    assert fetched.shipped_date == "2025-10-15"

def test_get_shipment_not_found(session):
    shipment_ctrl = ShipmentController(session)
    with pytest.raises(Exception):
        shipment_ctrl.get_by_id(4242)

def test_create_shipment_missing_order(session):
    shipment_ctrl = ShipmentController(session)
    # Не указан обязательный order_id
    with pytest.raises(ValueError):
        shipment_ctrl.create(order_id=None, shipped_date="2025-01-01")

def test_create_shipment_invalid_order(session):
    shipment_ctrl = ShipmentController(session)
    # Указан несуществующий order_id
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        shipment_ctrl.create(order_id=9999, shipped_date="2025-02-02")

def test_update_shipment_success(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="ShipSupplier3", contact="777")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-03-03")

    shipment_ctrl = ShipmentController(session)
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-03-04")
    # Обновляем дату отгрузки
    updated = shipment_ctrl.update(shipment.id, shipped_date="2025-03-05")
    assert updated.shipped_date == "2025-03-05"
    ship_db = session.query(Shipment).get(shipment.id)
    assert ship_db.shipped_date == "2025-03-05"

def test_update_shipment_not_found(session):
    shipment_ctrl = ShipmentController(session)
    with pytest.raises(Exception):
        shipment_ctrl.update(3030, shipped_date="2030-01-01")

def test_update_shipment_invalid_order(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="TempSup", contact="888")
    order = order_ctrl.create(supplier_id=supplier.id, date="2024-08-08")

    shipment_ctrl = ShipmentController(session)
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2024-08-09")
    # Попытка перепривязать shipment к несуществующему Order
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        shipment_ctrl.update(shipment.id, order_id=123456)

def test_delete_shipment_success(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="DelSup2", contact="999")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-04-01")
    shipment_ctrl = ShipmentController(session)
    shipment = shipment_ctrl.create(order_id=order.id, shipped_date="2025-04-02")
    shipment_ctrl.delete(shipment.id)
    assert session.query(Shipment).get(shipment.id) is None

def test_delete_shipment_not_found(session):
    shipment_ctrl = ShipmentController(session)
    with pytest.raises(Exception):
        shipment_ctrl.delete(7777)
