from datetime import datetime
import pytest
from controllers.OrderController import OrderController
from models.order import Order

def test_create_order_success(session):
    test_order = {
        'DateReg' : datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount' : 10,
        'Status' : True,
        'Employee' : 1,
        'Medicine' : 1,
    }
    #employee_ctrl = SupplierController(session)
    order_ctrl = OrderController(session)
    order = order_ctrl.create_order(test_order)
    assert order.id is not None
    ord_db = session.query(Order).get(order.id)
    assert ord_db.Employee == 1
    assert ord_db.DateReg == datetime.strptime('1999-12-31', '%Y-%m-%d').date()

def test_get_order_by_id(session):
    test_order = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 10,
        'Status': True,
        'Employee': 1,
        'Medicine': 1,
    }
    order_ctrl = OrderController(session)
    order = order_ctrl.create_order(test_order)
    fetched = order_ctrl.get_order_by_id(order.id)
    assert fetched.Employee == 1
    assert fetched.DateReg == datetime.strptime('1999-12-31', '%Y-%m-%d').date()

def test_get_order_not_found(session):
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.get_order_by_id(1234)

def test_create_order_missing_employee(session):
    test_order = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 10,
        'Status': True,
        'Employee': None,
        'Medicine': 1,
    }
    order_ctrl = OrderController(session)
    # Не передаем supplier_id (или передаем None) – должен быть отказ
    with pytest.raises(ValueError):
        order_ctrl.create_order(test_order)

def test_update_order_success(session):
    test_order = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 10,
        'Status': True,
        'Employee': 1,
        'Medicine': 1,
    }
    updated_data = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 20,
        'Status': False,
        'Employee': 2,
        'Medicine': 3,
    }
    order_ctrl = OrderController(session)
    order = order_ctrl.create_order(test_order)
    # Обновим количество заказа
    updated = order_ctrl.update_order(order.id, updated_data)
    assert updated.Amount == 20
    ord_db = session.query(Order).get(order.id)
    assert ord_db.Amount == 20

def test_update_order_not_found(session):
    test_order = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 10,
        'Status': True,
        'Employee': 1,
        'Medicine': 1,
    }
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.update_order(5555, test_order)

def test_delete_order_success(session):
    test_order = {
        'DateReg': datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
        'Amount': 10,
        'Status': True,
        'Employee': 1,
        'Medicine': 1,
    }
    order_ctrl = OrderController(session)
    order = order_ctrl.create_order(test_order)
    order_ctrl.delete_order(order.id)
    assert session.query(Order).get(order.id) is None

def test_delete_order_not_found(session):
    order_ctrl = OrderController(session)
    with pytest.raises(Exception):
        order_ctrl.delete_order(8888)
