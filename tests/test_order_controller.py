import pytest
import sqlalchemy
from controllers.OrderController import OrderController
from controllers.SupplierController import SupplierController
from models.order import Order

def test_create_order_success(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    # Создаем сначала поставщика, чтобы использовать его в заказе
    supplier = supplier_ctrl.create_supplier(name="SupplierX", contact="000")
    order = order_ctrl.create_order(supplier_id=supplier.id, date="2025-04-10")
    assert order.id is not None
    ord_db = session.query(Order).get(order.id)
    assert ord_db.supplier_id == supplier.id
    assert ord_db.date == "2025-04-10"

def test_get_order_by_id(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="SupplierY", contact="111")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-01-01")
    fetched = order_ctrl.get_by_id(order.id)
    assert fetched.supplier_id == supplier.id
    assert fetched.date == "2025-01-01"

def test_get_order_not_found(session):
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.get_by_id(1234)

def test_create_order_missing_supplier(session):
    order_ctrl = OrderController(session)
    # Не передаем supplier_id (или передаем None) – должен быть отказ
    with pytest.raises(ValueError):
        order_ctrl.create(supplier_id=None, date="2025-05-05")

def test_create_order_invalid_supplier(session):
    order_ctrl = OrderController(session)
    # Указываем несуществующий supplier_id
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        order_ctrl.create(supplier_id=9999, date="2025-06-01")

def test_update_order_success(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="SupplierZ", contact="222")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-07-07")
    # Обновим дату заказа
    updated = order_ctrl.update(order.id, date="2025-07-08")
    assert updated.date == "2025-07-08"
    ord_db = session.query(Order).get(order.id)
    assert ord_db.date == "2025-07-08"

def test_update_order_not_found(session):
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.update(5555, date="2030-01-01")

def test_update_order_invalid_supplier(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="TempSupplier", contact="333")
    order = order_ctrl.create(supplier_id=supplier.id, date="2024-12-12")
    # Попытка изменить привязку заказа на несуществующего поставщика
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        order_ctrl.update(order.id, supplier_id=123456)

def test_delete_order_success(session):
    supplier_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    supplier = supplier_ctrl.create(name="DelSup", contact="444")
    order = order_ctrl.create(supplier_id=supplier.id, date="2025-09-09")
    order_ctrl.delete(order.id)
    assert session.query(Order).get(order.id) is None

def test_delete_order_not_found(session):
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.delete(8888)
