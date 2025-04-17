from datetime import datetime
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RegistrationWindow(ctk.CTkToplevel):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller
        self.title("Регистрация")
        self.geometry("370x600")
        self.resizable(False, False)

        # Поля регистрации
        self.entries = {}
        fields = ["Фамилия", "Имя", "Телефон", "Должность", "Дата рождения", "Логин", "Пароль"]
        for field in fields:
            ctk.CTkLabel(self, text=field).pack(pady=(10, 0), anchor="w", padx=10)
            entry = ctk.CTkEntry(self, show="*" if field == "Пароль" else None)
            entry.pack(pady=5, padx=10, fill="x")
            self.entries[field] = entry

        ctk.CTkButton(self, text="Зарегистрироваться", command=self.on_register).pack(pady=20)

    def on_register(self):
        # TODO: реализовать регистрацию
        data = {
            'FName': self.entries['Имя'].get(),
            'LName': self.entries['Фамилия'].get(),
            'Number': self.entries['Телефон'].get(),
            'Position': self.entries['Должность'].get(),
            'Login': self.entries['Логин'].get(),
            'Pass': self.entries['Пароль'].get(),
            'DTB': datetime.strptime(self.entries['Дата рождения'].get(), '%d.%m.%Y').date(),
            'Admin': False
        }
        try:
            if self.controller:
                self.controller.create_employee(data)
        except Exception as e:
            CTkMessagebox(title="Ошибка", message=f"Произошла ошибка при регистрации: {e}")
        CTkMessagebox(title="Успех", message="Регистрация прошла успешно")
        self.destroy()
