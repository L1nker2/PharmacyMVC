import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from controllers.ClientController import ClientController
from controllers.EmployeeController import EmployeeController
from controllers.MedicineController import MedicineController
from controllers.SupplierController import SupplierController
from controllers.OrderController import OrderController
from models.employee import Employee
from models.medicine import Medicine
from models.supplier import Supplier
from models.client import Client
from models.order import Order
from models.base import Base

class UserFrame(ctk.CTkFrame):
    def __init__(self, master, session, client, *args, **kwargs):
        """
        Виджет для отображения данных пользователя.

        :param master: родительский виджет.
        :param client: объект класса Client с данными пользователя.
        """
        super().__init__(master, *args, **kwargs)
        self.client = client
        self.edit_panel = None
        self.topup_panel = None
        self.password_visible = False
        self.session = session
        self.create_widgets()

    def create_widgets(self):
        # Отображение основных данных пользователя
        self.label_fname = ctk.CTkLabel(self, text=f"Имя: {self.client.FName}")
        self.label_fname.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.label_lname = ctk.CTkLabel(self, text=f"Фамилия: {self.client.LName}")
        self.label_lname.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.label_number = ctk.CTkLabel(self, text=f"Номер телефона: {self.client.Number}")
        self.label_number.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.label_balance = ctk.CTkLabel(self, text=f"Баланс: {self.client.Balance}")
        self.label_balance.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        self.label_login = ctk.CTkLabel(self, text=f"Логин: {self.client.Login}")
        self.label_login.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        # Кнопки "Редактировать" и "Пополнить баланс"
        self.edit_button = ctk.CTkButton(self, text="Редактировать", command=self.show_edit_panel)
        self.edit_button.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.topup_button = ctk.CTkButton(self, text="Пополнить баланс", command=self.show_topup_panel)
        self.topup_button.grid(row=6, column=1, padx=10, pady=10, sticky="w")

    def show_edit_panel(self):
        if self.edit_panel is None:
            self.edit_panel = ctk.CTkFrame(self)
            self.edit_panel.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

            # Поля редактирования (предзаполнены текущими данными)
            # Имя
            ctk.CTkLabel(self.edit_panel, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.edit_fname = ctk.CTkEntry(self.edit_panel, width=200)
            self.edit_fname.insert(0, self.client.FName)
            self.edit_fname.grid(row=0, column=1, padx=5, pady=5)
            # Фамилия
            ctk.CTkLabel(self.edit_panel, text="Фамилия:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.edit_lname = ctk.CTkEntry(self.edit_panel, width=200)
            self.edit_lname.insert(0, self.client.LName)
            self.edit_lname.grid(row=1, column=1, padx=5, pady=5)
            # Номер телефона
            ctk.CTkLabel(self.edit_panel, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.edit_number = ctk.CTkEntry(self.edit_panel, width=200)
            self.edit_number.insert(0, self.client.Number)
            self.edit_number.grid(row=2, column=1, padx=5, pady=5)
            # Баланс
            ctk.CTkLabel(self.edit_panel, text="Баланс:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.edit_balance = ctk.CTkEntry(self.edit_panel, width=200)
            self.edit_balance.insert(0, str(self.client.Balance))
            self.edit_balance.grid(row=3, column=1, padx=5, pady=5)
            # Логин
            ctk.CTkLabel(self.edit_panel, text="Логин:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
            self.edit_login = ctk.CTkEntry(self.edit_panel, width=200)
            self.edit_login.insert(0, self.client.Login)
            self.edit_login.grid(row=4, column=1, padx=5, pady=5)
            # Пароль
            ctk.CTkLabel(self.edit_panel, text="Пароль:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
            self.edit_password = ctk.CTkEntry(self.edit_panel, width=200, show="*")
            self.edit_password.insert(0, self.client.Pass)
            self.edit_password.grid(row=5, column=1, padx=5, pady=5)

            # Кнопки редактирования
            self.save_button = ctk.CTkButton(self.edit_panel, text="Сохранить", command=self.save_data)
            self.save_button.grid(row=6, column=0, padx=5, pady=10)

            self.delete_button = ctk.CTkButton(self.edit_panel, text="Удалить", command=self.delete_data)
            self.delete_button.grid(row=6, column=1, padx=5, pady=10)

            self.cancel_button = ctk.CTkButton(self.edit_panel, text="Отмена", command=self.hide_edit_panel)
            self.cancel_button.grid(row=6, column=2, padx=5, pady=10)

    def hide_edit_panel(self):
        if self.edit_panel:
            self.edit_panel.destroy()
            self.edit_panel = None

    def save_data(self):
        # Обновление данных клиента
        updated_data={
            'FName': self.edit_fname.get(),
            'LName': self.edit_lname.get(),
            'Number': self.edit_number.get(),
            'Login': self.edit_login.get(),
            'Pass': self.edit_password.get(),
            'Balance': self.edit_balance.get()
        }
        controller = ClientController(self.session)
        controller.update_client(self.client.id, updated_data)

        self.client.FName = self.edit_fname.get()
        self.client.LName = self.edit_lname.get()
        self.client.Number = self.edit_number.get()
        self.client.Balance = self.edit_balance.get()
        self.client.Login = self.edit_login.get()
        self.client.Pass = self.edit_password.get()

        # Обновляем отображаемые метки
        self.label_fname.configure(text=f"Имя: {self.client.FName}")
        self.label_lname.configure(text=f"Фамилия: {self.client.LName}")
        self.label_number.configure(text=f"Номер телефона: {self.client.Number}")
        self.label_balance.configure(text=f"Баланс: {self.client.Balance}")
        self.label_login.configure(text=f"Логин: {self.client.Login}")


        self.hide_edit_panel()

    def delete_data(self):
        msg = CTkMessagebox(title="Подтверждение удаления", message="Вы действительно ходите удалить профиль?",
                      icon="info", option_1="Да", option_2="Отмена")
        # Здесь можно реализовать удаление аккаунта или очистку данных
        response=msg.get()
        if response == "Да":
            controller = ClientController(self.session)
            controller.delete_client(self.client.id)
            self.winfo_toplevel().destroy()
            self.master.destroy()
        else:
            self.hide_edit_panel()

    def show_topup_panel(self):
        if self.topup_panel is None:
            self.topup_panel = ctk.CTkFrame(self)
            self.topup_panel.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

            ctk.CTkLabel(self.topup_panel, text="Сумма пополнения:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.topup_entry = ctk.CTkEntry(self.topup_panel, width=150)
            self.topup_entry.grid(row=0, column=1, padx=5, pady=5)

            self.topup_confirm_button = ctk.CTkButton(self.topup_panel, text="Подтвердить", command=self.confirm_topup)
            self.topup_confirm_button.grid(row=0, column=2, padx=5, pady=5)

            self.topup_cancel_button = ctk.CTkButton(self.topup_panel, text="Отмена", command=self.hide_topup_panel)
            self.topup_cancel_button.grid(row=0, column=3, padx=5, pady=5)

    def hide_topup_panel(self):
        if self.topup_panel:
            self.topup_panel.destroy()
            self.topup_panel = None

    def confirm_topup(self):
        try:
            amount = float(self.topup_entry.get())
            if amount <= 0:
                CTkMessagebox(title="Предупреждение", message="Введите положительное число", icon="warning")
                return
        except ValueError:
            CTkMessagebox(title="Предупреждение", message="Некорректное значение", icon="warning")
            print("")
            return

        # Обновляем баланс клиента
        try:
            current_balance = float(self.client.Balance)
        except ValueError:
            current_balance = 0.0
        new_balance = current_balance + amount
        self.client.Balance = new_balance

        self.label_balance.configure(text=f"Баланс: {self.client.Balance}")
        CTkMessagebox(title="Успешно", message=f"Баланс пополнен, новая сумма: {new_balance}", icon="info")
        self.hide_topup_panel()
