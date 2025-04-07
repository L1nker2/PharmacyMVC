from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from models.medicine import Medicine
from typing import List, Optional


class MedicineController:
    def __init__(self, session: Session):
        self.session = session

    def create_medicine(self, mname: str, price: float, description: str,
                        count: int, category: str, bbt: str, supplier_id: int) -> Medicine:
        """
        Создание нового лекарства
        """
        try:
            medicine = Medicine(
                MName=mname,
                Price=price,
                Description=description,
                Count=count,
                Category=category,
                BBT=bbt,
                Supplier=supplier_id
            )
            self.session.add(medicine)
            self.session.commit()
            return medicine
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка создания лекарства: {str(e)}")

    def get_medicine_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """
        Получение лекарства по ID
        """
        try:
            return self.session.get(Medicine, medicine_id)
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения лекарства: {str(e)}")

    def update_medicine(self, medicine_id: int, **kwargs) -> Medicine:
        """
        Обновление данных лекарства
        """
        try:
            medicine = self.session.get(Medicine, medicine_id)
            if not medicine:
                raise ValueError("Лекарство не найдено")

            for key, value in kwargs.items():
                if hasattr(medicine, key):
                    setattr(medicine, key, value)

            self.session.commit()
            return medicine
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка обновления лекарства: {str(e)}")

    def delete_medicine(self, medicine_id: int) -> bool:
        """
        Удаление лекарства
        """
        try:
            medicine = self.session.get(Medicine, medicine_id)
            if not medicine:
                return False

            self.session.delete(medicine)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"Ошибка удаления лекарства: {str(e)}")

    def get_all_medicines(self, category: str = None, supplier_id: int = None) -> List[Medicine]:
        """
        Получение списка лекарств с опциональной фильтрацией
        """
        try:
            query = select(Medicine)

            if category:
                query = query.where(Medicine.Category == category)

            if supplier_id:
                query = query.where(Medicine.Supplier == supplier_id)

            return list(self.session.scalars(query).all())
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка получения списка лекарств: {str(e)}")

    def get_medicines_expiring_after(self, expiration_date: str) -> List[Medicine]:
        """
        Получение лекарств с сроком годности после указанной даты
        """
        try:
            query = select(Medicine).where(Medicine.BBT > expiration_date)
            return list(self.session.scalars(query).all())
        except SQLAlchemyError as e:
            raise ValueError(f"Ошибка фильтрации по сроку годности: {str(e)}")