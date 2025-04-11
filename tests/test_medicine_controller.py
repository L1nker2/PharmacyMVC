import pytest
import sqlalchemy
from controllers.MedicineController import MedicineController
from models.medicine import Medicine

def test_create_medicine_success(session):
    test_data = {
        'MName' : "Aspirin",
        'Price' : 10,
        'Count' : 1,
        'Description' : 'Aspirin',
        'Category' : "test",
        'Supplier' : 1,
        'BT' : "12",
    }
    controller = MedicineController(session)
    med = controller.create_medicine(test_data)
    assert med.id is not None
    med_db = session.query(Medicine).get(med.id)
    assert med_db.MName == "Aspirin"
    assert med_db.Price == 10.0

def test_get_medicine_by_id(session):
    test_data = {
        'MName': "Paracetamol",
        'Price': 5.5,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    med = controller.create_medicine(test_data)
    fetched = controller.get_medicine_by_id(med.id)
    assert fetched.MName == "Paracetamol"
    assert fetched.Price == 5.5

def test_get_medicine_not_found(session):
    controller = MedicineController(session)
    with pytest.raises(Exception):
        controller.get_medicine_by_id(42)

def test_create_medicine_missing_name(session):
    test_data = {
        'MName': "",
        'Price': 10,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    with pytest.raises(ValueError):
        controller.create_medicine(test_data)

def test_create_medicine_negative_price(session):
    test_data = {
        'MName': "Aspirin",
        'Price': -10,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    # Отрицательная цена недопустима
    with pytest.raises(ValueError):
        controller.create_medicine(test_data)

def test_create_medicine_duplicate_name(session):
    test_data = {
        'MName': "UniqueMed",
        'Price': 10,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    test_data2 = {
        'MName': "UniqueMed",
        'Price': 15,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    controller.create_medicine(test_data)
    with pytest.raises(sqlalchemy.exc.IntegrityError) as excinfo:
        controller.create_medicine(test_data2)
    assert "UNIQUE constraint failed" in str(excinfo.value)

def test_update_medicine_success(session):
    test_data = {
        'MName': "Tempra",
        'Price': 1,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    updated_data = {
        'MName': "Tempra",
        'Price': 10,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    med = controller.create_medicine(test_data)
    updated = controller.update_medicine(med.id, updated_data)
    assert updated.Price == 10
    med_db = session.query(Medicine).get(med.id)
    assert med_db.Price == 10

def test_update_medicine_not_found(session):
    test_data = {
        'MName': "Tempra",
        'Price': 1,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    with pytest.raises(Exception):
        controller.update_medicine(777, test_data)

def test_update_medicine_invalid_price(session):
    test_data = {
        'MName': "VitaminC",
        'Price': 3,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    test_data2 = {
        'MName': "VitaminC",
        'Price': -1,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    med = controller.create_medicine(test_data)
    # Обновление на отрицательную цену должно давать ошибку
    with pytest.raises(ValueError):
        controller.update_medicine(med.id, test_data2)

def test_delete_medicine_success(session):
    test_data = {
        'MName': "Tempra",
        'Price': 1,
        'Count': 1,
        'Description': 'Aspirin',
        'Category': "test",
        'Supplier': 1,
        'BT': "12",
    }
    controller = MedicineController(session)
    med = controller.create_medicine(test_data)
    controller.delete_medicine(med.id)
    assert session.query(Medicine).get(med.id) is None

def test_delete_medicine_not_found(session):
    controller = MedicineController(session)
    with pytest.raises(Exception):
        controller.delete_medicine(999)
