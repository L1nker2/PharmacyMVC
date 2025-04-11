import sqlalchemy
from sqlalchemy.orm import Session, load_only
from typing import Optional, Type
from models.medicine import Medicine


class MedicineController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_medicine(self, medicine_data: dict) -> Medicine:
        """Создает новый медикамент."""
        if medicine_data['MName'] == '' or medicine_data['Price'] == ''\
            or medicine_data['Count'] == '' or medicine_data['Description'] == ''\
            or medicine_data['Category'] == '' or medicine_data['BT'] == '' or medicine_data['Supplier'] == '':
            raise ValueError("Fill in all fields")
        if medicine_data['Price'] < 0 or medicine_data['Count'] < 0:
            raise ValueError("The value cannot be less than zero.")
        if not self.is_name_unique(medicine_data['MName']):
            raise sqlalchemy.exc.IntegrityError(statement="UNIQUE constraint failed", params="UNIQUE constraint failed",
                                                orig="UNIQUE constraint failed")
        medicine = Medicine(**medicine_data)
        self.db.add(medicine)
        self.db.commit()
        self.db.refresh(medicine)
        return medicine

    def get_medicine_by_id(self, medicine_id: int) -> Type[Medicine]:
        """Возвращает медикамент по ID или None, если не найден."""
        medicine = self.db.get(Medicine, medicine_id)
        if medicine is None:
            raise ValueError("Medicine not found")
        else: return medicine

    def update_medicine(self, medicine_id: int, update_data: dict) -> Type[Medicine] | None:
        """Обновляет данные медикамента по ID. Возвращает обновленный объект или None."""
        if update_data['Price'] < 0 or update_data['Count'] < 0:
            raise ValueError("The value cannot be less than zero.")
        medicine = self.db.get(Medicine, medicine_id)
        if not medicine:
            raise ValueError("Medicine not found")
        for field, value in update_data.items():
            setattr(medicine, field, value)
        self.db.commit()
        self.db.refresh(medicine)
        return medicine

    def delete_medicine(self, medicine_id: int) -> Type[Medicine] | None:
        """Удаляет медикамент по ID. Возвращает удалённый объект или None."""
        medicine = self.db.get(Medicine, medicine_id)
        if not medicine:
            raise ValueError("Medicine not found")
        self.db.delete(medicine)
        self.db.commit()
        return medicine

    def get_all(self) -> list[Type[Medicine]]:
        """Возвращает список всех медикаментов (с ограниченным набором полей)."""
        return self.db.query(Medicine).options(
            load_only(Medicine.id, Medicine.MName, Medicine.Price)
        ).all()

    def is_name_unique(self, name: str) -> bool:
        """Проверяет, уникален ли указанный логин (True, если такого логина нет в базе)."""
        existing = self.db.query(Medicine).filter(Medicine.MName == name).first()
        return existing is None