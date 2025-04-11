import pytest
from datetime import date, datetime
from sqlalchemy import inspect
from controllers.ShipmentController import ShipmentController
from models.shipment import Shipment
from models.shipment_item import ShipmentItem
from models.supplier import Supplier
from models.employee import Employee
from models.medicine import Medicine

@pytest.fixture
def controller(session):
    return ShipmentController(session)

def test_create_shipment(controller, session):
    # Setup related entities
    supplier = Supplier(id = 1, CompName = "Test Supplier", Address = "Test Address",
                        Number = "Test Number", INN = "Test INN")
    employee = Employee(id = 1, FName = "Test FName",
                        LName = "Test LName", Number = "Test Number",
                        Position = "Test Position", Login = "Test Login",
                        Pass = "Test Pass",
                        DTB = datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin = False)
    medicine = Medicine(id = 1, MName = "Test MName",
                        Price = 100, Count = 100,
                        Description = "Test Description",
                        Category = "Test Category", BT = "Test BT",
                        Supplier = 1)
    session.add_all([supplier, employee, medicine])
    session.commit()

    # Test data
    shipment_data = {
        "Supplier": supplier.id,
        "Employee": employee.id,
        "DateReg": date.today(),
        "Amount": 1000,
        "Status": True
    }
    items = [{"medication_id": medicine.id, "quantity": 10}]

    # Create shipment
    shipment = controller.create_shipment(shipment_data, items)

    # Assert shipment
    assert shipment is not None
    assert shipment.id is not None
    assert shipment.Supplier == supplier.id
    assert shipment.Employee == employee.id
    assert shipment.Amount == 1000

    # Assert shipment items
    assert len(shipment.items) == 1
    item = shipment.items[0]
    assert item.Medicine == medicine.id
    assert item.Quantity == 10
    assert shipment.get_total_quantity() == 10

    # Check database state
    db_items = session.query(ShipmentItem).all()
    assert len(db_items) == 1

def test_get_shipment_by_id(controller, session):
    # Create test shipment
    supplier = Supplier(id=1, CompName="Test Supplier", Address="Test Address",
                        Number="Test Number", INN="Test INN")
    employee = Employee(id=1, FName="Test FName",
                        LName="Test LName", Number="Test Number",
                        Position="Test Position", Login="Test Login",
                        Pass="Test Pass",
                        DTB=datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin = False)

    session.add_all([supplier, employee])
    session.commit()

    shipment = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date.today(),
        Amount=500,
        Status=False
    )
    session.add(shipment)
    session.commit()

    # Test existing shipment
    result = controller.get_shipment_by_id(shipment.id)
    assert result.id == shipment.id
    assert result.Amount == 500

    # Test non-existent shipment
    assert controller.get_shipment_by_id(999) is None

def test_update_shipment(controller, session):
    # Create test shipment
    supplier = Supplier(id=1, CompName="Test Supplier", Address="Test Address",
                        Number="Test Number", INN="Test INN")
    employee = Employee(id=1, FName="Test FName",
                        LName="Test LName", Number="Test Number",
                        Position="Test Position", Login="Test Login",
                        Pass="Test Pass",
                        DTB=datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin = False)
    session.add_all([supplier, employee])
    session.commit()

    shipment = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date.today(),
        Amount=200,
        Status=False
    )
    session.add(shipment)
    session.commit()

    # Update data
    update_data = {"Amount": 300, "Status": True}
    updated = controller.update_shipment(shipment.id, update_data)

    # Assert updates
    assert updated.Amount == 300
    assert updated.Status is True
    db_shipment = session.get(Shipment, shipment.id)
    assert db_shipment.Amount == 300

    # Test non-existent shipment
    assert controller.update_shipment(999, {"Amount": 100}) is None

def test_delete_shipment(controller, session):
    # Create test shipment with item
    supplier = Supplier(id=1, CompName="Test Supplier", Address="Test Address",
                        Number="Test Number", INN="Test INN")
    employee = Employee(id=1, FName="Test FName",
                        LName="Test LName", Number="Test Number",
                        Position="Test Position", Login="Test Login",
                        Pass="Test Pass",
                        DTB=datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin = False)
    medicine = Medicine(id=1, MName="Test MName",
                        Price=100, Count=100,
                        Description="Test Description",
                        Category="Test Category", BT="Test BT",
                        Supplier=1)
    session.add_all([supplier, employee, medicine])
    session.commit()

    shipment = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date.today(),
        Amount=100,
        Status=True
    )
    session.add(shipment)
    session.flush()  # Get shipment ID

    item = ShipmentItem(Shipment=shipment.id, Medicine=medicine.id, Quantity=5)
    session.add(item)
    session.commit()

    # Delete shipment
    deleted = controller.delete_shipment(shipment.id)
    assert deleted.id == shipment.id

    # Verify deletion
    assert session.get(Shipment, shipment.id) is None
    # Verify items remain
    # При удалении поставки, так же удаляются связанные записи в ShipmentItems
    assert session.query(ShipmentItem).count() == 0

def test_get_all_shipments(controller, session):
    # Create test data
    supplier = Supplier(id=1, CompName="Test Supplier", Address="Test Address",
                        Number="Test Number", INN="Test INN")
    employee = Employee(id=1, FName="Test FName",
                        LName="Test LName", Number="Test Number",
                        Position="Test Position", Login="Test Login",
                        Pass="Test Pass",
                        DTB=datetime.strptime('1999-12-31', '%Y-%m-%d').date(),
                        Admin = False)
    session.add_all([supplier, employee])
    session.commit()

    shipment1 = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date(2023, 1, 1),
        Amount=100,
        Status=True
    )
    shipment2 = Shipment(
        Supplier=supplier.id,
        Employee=employee.id,
        DateReg=date(2023, 1, 2),
        Amount=200,
        Status=False
    )
    session.add_all([shipment1, shipment2])
    session.commit()

    # Test get all
    shipments = controller.get_all()
    assert len(shipments) == 2

    # Verify loaded fields
    for shipment in shipments:
        assert hasattr(shipment, "id")
        assert hasattr(shipment, "Supplier")
        assert hasattr(shipment, "DateReg")

        # Проверяем НЕзагруженные поля
        insp = inspect(shipment)
        unloaded = insp.unloaded

        # Поля, которые НЕ должны быть загружены
        assert "Amount" in unloaded
        assert "Status" in unloaded
        assert "Employee" in unloaded  # Если Employee тоже не указан в load_only

        # Поля, которые ДОЛЖНЫ быть загружены
        assert "id" not in unloaded
        assert "Supplier" not in unloaded
        assert "DateReg" not in unloaded