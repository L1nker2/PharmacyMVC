import pytest
import sqlalchemy
from controllers.SupplierController import SupplierController
from models.supplier import Supplier

def test_create_supplier_success(session):
    controller = SupplierController(session)
    supplier = controller.create(name="PharmaCorp", contact="123-456-789")
    assert supplier.id is not None
    # Проверяем наличие в базе данных
    sup_db = session.query(Supplier).get(supplier.id)
    assert sup_db.name == "PharmaCorp"
    assert sup_db.contact == "123-456-789"

def test_get_supplier_by_id(session):
    controller = SupplierController(session)
    sup = controller.create(name="MedSuppliers LLC", contact="987-654-321")
    fetched = controller.get_by_id(sup.id)
    assert fetched is not None
    assert fetched.name == "MedSuppliers LLC"
    assert fetched.contact == "987-654-321"

def test_get_supplier_not_found(session):
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.get_by_id(5555)

def test_create_supplier_missing_name(session):
    controller = SupplierController(session)
    with pytest.raises(ValueError):
        controller.create(name=None, contact="no-name contact")

def test_create_supplier_duplicate_name(session):
    controller = SupplierController(session)
    controller.create(name="DupSupplier", contact="111")
    with pytest.raises(sqlalchemy.exc.IntegrityError) as excinfo:
        controller.create(name="DupSupplier", contact="222")
    assert "UNIQUE constraint failed" in str(excinfo.value)  # нарушение уникальности имени

def test_update_supplier_success(session):
    controller = SupplierController(session)
    sup = controller.create(name="ChemCo", contact="000-000")
    updated = controller.update(sup.id, contact="111-111")
    # Проверяем, что контакт обновился
    assert updated.contact == "111-111"
    sup_db = session.query(Supplier).get(sup.id)
    assert sup_db.contact == "111-111"

def test_update_supplier_not_found(session):
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.update(999, name="NoOne")

def test_update_supplier_invalid_data(session):
    controller = SupplierController(session)
    sup = controller.create(name="ValidName", contact="123")
    # Пустое имя недопустимо
    with pytest.raises(ValueError):
        controller.update(sup.id, name="")

def test_delete_supplier_success(session):
    controller = SupplierController(session)
    sup = controller.create(name="DeleteMe", contact="321-000")
    controller.delete(sup.id)
    assert session.query(Supplier).get(sup.id) is None

def test_delete_supplier_not_found(session):
    controller = SupplierController(session)
    with pytest.raises(Exception):
        controller.delete(10101)
