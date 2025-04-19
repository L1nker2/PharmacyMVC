import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class Security:
    # Конфигурация
    _KEY_FILE = "encryption.key"
    _SALT_FILE = "encryption.salt"
    _ITERATIONS = 100_000
    _cipher = None

    @classmethod
    def initialize(cls):
        """Инициализация системы шифрования"""
        if cls._cipher is None:
            key = cls._load_or_generate_key()
            cls._cipher = Fernet(key)

    @classmethod
    def _load_or_generate_key(cls) -> bytes:
        """Загружает или генерирует ключ шифрования"""
        key_path = Path(cls._KEY_FILE)
        salt_path = Path(cls._SALT_FILE)

        # Если файлы существуют - загружаем ключ
        if key_path.exists() and salt_path.exists():
            with open(salt_path, 'rb') as f:
                salt = f.read()
            with open(key_path, 'rb') as f:
                return f.read()

        # Генерируем новый ключ
        return cls.generate_new_key()

    @classmethod
    def generate_new_key(cls) -> bytes:
        """Генерирует новый ключ шифрования и сохраняет в файл"""
        # Генерируем случайную соль
        salt = os.urandom(16)

        # Создаем ключ из пароля (можно использовать любой статический пароль)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=cls._ITERATIONS,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"default_password"))

        # Сохраняем соль и ключ
        with open(cls._SALT_FILE, 'wb') as f:
            os.chmod(cls._SALT_FILE, 0o600)
            f.write(salt)

        with open(cls._KEY_FILE, 'wb') as f:
            os.chmod(cls._KEY_FILE, 0o600)
            f.write(key)

        return key

    @staticmethod
    def encrypt_password(password: str) -> str:
        """Шифрует пароль"""
        Security.initialize()
        return Security._cipher.encrypt(password.encode()).decode()

    @staticmethod
    def decrypt_password(encrypted: str) -> str:
        """Дешифрует пароль"""
        try:
            Security.initialize()
            return Security._cipher.decrypt(encrypted.encode()).decode()
        except Exception as e:
            print(f"Ошибка дешифровки: {e}")
            return ""

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Алиас для шифрования пароля"""
        return Security.encrypt_password(password)

    @staticmethod
    def verify_password(password: str, encrypted: str) -> bool:
        """Проверяет совпадение пароля с зашифрованной версией"""
        return password == Security.decrypt_password(encrypted)

    @classmethod
    def rotate_key(cls, new_password: str = None):
        """Генерирует новый ключ шифрования"""
        # Удаляем старые файлы
        for f in [cls._KEY_FILE, cls._SALT_FILE]:
            if os.path.exists(f):
                os.remove(f)

        # Генерируем новый ключ
        cls._cipher = None
        cls.initialize()
        print("Новый ключ шифрования успешно создан!")

Security.initialize()