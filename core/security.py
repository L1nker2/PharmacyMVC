import hashlib
import os
import binascii


class Security:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Простое хэширование пароля с солью"""
        salt = os.urandom(16)  # Генерация случайной соли
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # Количество итераций
        )
        return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(key).decode()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Проверка пароля против хэша"""
        try:
            salt, key = hashed.split('$')
            salt = binascii.unhexlify(salt.encode())
            key = binascii.unhexlify(key.encode())

            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )
            return new_key == key
        except Exception as e:
            print(e)
            return False