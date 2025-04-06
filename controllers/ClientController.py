from sqlalchemy.orm import Session
from models.client import Client
from core.security import Security
from typing import Optional
import decimal

class ClientController:
    def __init__(self, db_session: Session):
        self.db = db_session

    # Основные CRUD операции
    def create_client(self, client_data: dict) -> Client:
        if not self.is_login_unique(client_data['Login']):
            raise ValueError("Login already exists")

        client_data['Pass'] = Security.get_password_hash(client_data['Pass'])
        new_client = Client(**client_data)  # Теперь Client - это класс
        self.db.add(new_client)
        self.db.commit()
        return new_client

    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Получение клиента по ID"""
        return self.db.query(Client).filter(Client.id == client_id).first()

    def update_client(self, client_id: int, update_data: dict) -> Client:
        """Обновление данных клиента"""
        client = self.get_client_by_id(client_id)
        for key, value in update_data.items():
            if key == 'Pass':  # Особый случай для пароля
                value = Security.get_password_hash(value)
            setattr(client, key, value)
        self.db.commit()
        return client

    def delete_client(self, client_id: int) -> bool:
        """Удаление клиента"""
        client = self.get_client_by_id(client_id)
        self.db.delete(client)
        self.db.commit()
        return True

    # Бизнес-логика
    def authenticate(self, login: str, password: str) -> Optional[Client]:
        """Аутентификация клиента"""
        client = self.db.query(Client).filter(Client.Login == login).first()
        if client and Security.verify_password(password, client.Pass):
            return client
        raise ValueError("Invalid password")

    def update_balance(self, client_id: int, amount: float) -> Client:
        """Изменение баланса клиента"""
        client = self.get_client_by_id(client_id)
        client.Balance += decimal.Decimal(amount)
        self.db.commit()
        return client

    # Валидация и утилиты
    def is_login_unique(self, login: str) -> bool:
        """Проверка уникальности логина"""
        return not self.db.query(Client).filter(Client.Login == login).first()
