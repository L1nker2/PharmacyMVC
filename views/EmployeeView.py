import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
from views.customUI.SortableTableFrame import SortableTableFrame

class EmployeeFrame(ctk.CTkFrame):
    def __init__(self, master, session, *args, **kwargs):
        """
        Виджет для отображения сотрудников.

        :param master: родительский виджет.
        :param employee: объект класса Employee с данными пользователя.
        """
        super().__init__(master, *args, **kwargs)
        self.session = session
        self.create_widgets()

    def edit_event(self):
        pass
    def delete_event(self, id):
        msg = CTkMessagebox(title="Подтверждение удаления", message="Вы действительно ходите удалить профиль?",
                            icon="info", option_1="Да", option_2="Отмена")
        response = msg.get()
        if response == "Да":
            controller = EmployeeController(self.session)
            controller.delete_employee(id)
            for widget in self.winfo_children():
                widget.destroy()
            self.create_widgets()
        else:
            return

    def create_widgets(self):
        controller = EmployeeController(self.session)
        employees = controller.get_all()

        headers = ["Айди", "Имя", "Фамилия", "Телефон", "Должность", "Логин", "Дата рождения"]
        table = SortableTableFrame(master=self, headers=headers, data=employees,
                                   edit_event=self.edit_event, delete_event=self.delete_event)
        table.pack(padx=20, pady=20, fill="both", expand=True)
root = ctk.CTk()
root.geometry("500x600")
root.title("test")

# Создаем виджет авторизации
engine = create_engine("mysql+mysqldb://python:python@localhost/apteka")
Session = sessionmaker(bind=engine)
session = Session()
auth_frame = EmployeeFrame(root, session)
auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

root.mainloop()