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
    def __init__(self, master: ctk.CTk, session, client, *args, **kwargs):
        """
        Виджет для отображения сотрудников.

        :param master: родительский виджет.
        :param client: объект класса Client с данными пользователя.
        """
        super().__init__(master, *args, **kwargs)
        master.geometry('вставить значение')
        self.session = session
        self.create_widgets()

    def create_widgets(self):
        pass