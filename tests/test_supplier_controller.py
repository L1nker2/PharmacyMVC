import pytest
import sqlalchemy
from controllers.SupplierController import SupplierController
from models.supplier import Supplier

def test_create_supplier_success(session):
    test_data = {
        'CompName': "PharmaCorp",
        'Address': "testAddress",
        'Number': "123-456-789",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    supplier = controller.create_supplier(test_data)
    assert supplier.id is not None
    # Проверяем наличие в базе данных
    sup_db = session.query(Supplier).get(supplier.id)
    assert sup_db.CompName == "PharmaCorp"
    assert sup_db.Number == "123-456-789"

def test_get_supplier_by_id(session):
    test_data = {
        'CompName': "MedSuppliers LLC",
        'Address': "testAddress",
        'Number': "987-654-321",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    sup = controller.create_supplier(test_data)
    fetched = controller.get_supplier_by_id(sup.id)
    assert fetched is not None
    assert fetched.CompName == "MedSuppliers LLC"
    assert fetched.Number == "987-654-321"

def test_get_supplier_not_found(session):
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.get_supplier_by_id(5555)

def test_create_supplier_missing_name(session):
    test_data = {
        'CompName': "",
        'Address': "testAddress",
        'Number': "no-name contact",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    with pytest.raises(ValueError):
        controller.create_supplier(test_data)

def test_create_supplier_duplicate_name(session):
    test_data = {
        'CompName': "DupSupplier",
        'Address': "testAddress",
        'Number': "111",
        'INN': "testINN",
    }
    test_data2 = {
        'CompName': "DupSupplier",
        'Address': "testAddress",
        'Number': "222",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    controller.create_supplier(test_data)
    with pytest.raises(sqlalchemy.exc.IntegrityError) as excinfo:
        controller.create_supplier(test_data2)
    assert "UNIQUE constraint failed" in str(excinfo.value)  # нарушение уникальности имени

def test_update_supplier_success(session):
    test_data = {
        'CompName': "ChemCo",
        'Address': "testAddress",
        'Number': "000-000",
        'INN': "testINN",
    }
    updated_data = {
        'CompName': "ChemCo",
        'Address': "testAddress",
        'Number': "111-111",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    sup = controller.create_supplier(test_data)
    updated = controller.update_supplier(sup.id, updated_data)
    # Проверяем, что контакт обновился
    assert updated.Number == "111-111"
    sup_db = session.query(Supplier).get(sup.id)
    assert sup_db.Number == "111-111"

def test_update_supplier_not_found(session):
    test_data = {
        'CompName': "",
        'Address': "testAddress",
        'Number': "000-000",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.update_supplier(999, test_data)

def test_update_supplier_invalid_data(session):
    test_data = {
        'CompName': "ValidName",
        'Address': "testAddress",
        'Number': "123",
        'INN': "testINN",
    }
    updated_data = {
        'CompName': "",
        'Address': "testAddress",
        'Number': "000-000",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    sup = controller.create_supplier(test_data)
    # Пустое имя недопустимо
    with pytest.raises(ValueError):
        controller.update_supplier(sup.id, updated_data)

def test_delete_supplier_success(session):
    test_data = {
        'CompName': "DeleteMe",
        'Address': "testAddress",
        'Number': "321-000",
        'INN': "testINN",
    }
    controller = SupplierController(session)
    sup = controller.create_supplier(test_data)
    controller.delete_supplier(sup.id)
    assert session.query(Supplier).get(sup.id) is None

def test_delete_supplier_not_found(session):
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.delete_supplier(10101)
