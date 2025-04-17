import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from views.customUI.RegistrationWindow import RegistrationWindow
from models.employee import Employee

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller
        self.title("Логин")
        self.geometry("150x250")
        self.resizable(True, True)

        # Метки и поля ввода
        ctk.CTkLabel(self, text="Логин").pack(pady=(10, 0))
        self.login_entry = ctk.CTkEntry(self)
        self.login_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self, text="Пароль").pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=5, padx=10, fill="x")

        # Кнопки
        ctk.CTkButton(self, text="Войти", command=self.on_login).pack(pady=(15, 5))
        ctk.CTkButton(self, text="Регистрация", command=self.on_register).pack(pady=5)

    def on_login(self):
        # TODO: проверка логина и пароля через контроллер
        # при успешном входе раскрываем главное окно и закрываем это
        employee = None
        login = self.login_entry.get()
        password = self.password_entry.get()
        if self.controller:
            employee = self.controller.authenticate(
                login, password
            )

        if isinstance(employee, Employee):
            self.destroy()
            # показываем главное окно
            self.master.deiconify()
        else:
            CTkMessagebox(title="Предупреждение", message="Пользователь не найден")

    def on_register(self):
        # открываем окно регистрации
        if self.controller and hasattr(self.controller, 'open_registration'):
            self.controller.open_registration()
        else:
            RegistrationWindow(self, self.controller)