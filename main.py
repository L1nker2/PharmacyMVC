import logging
from datetime import date

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
from views.customUI.LoginFrame import AuthFrame
from views.ClientView import UserFrame


engine = create_engine("mysql+mysqldb://python:python@localhost/apteka")
Session = sessionmaker(bind=engine)
session = Session()
client_controller=ClientController(session)
employee_controller=EmployeeController(session)

class main_window:
    is_login = False
    who_login = ""
    client = None

    def __init__(self):
        # Функция обратного вызова для входа
        def login_callback(login, password, role):
            nonlocal auth_frame, root  # Даем доступ к переменным auth_frame и root
            try:
                if role == "Сотрудник":
                    employee = employee_controller.authenticate(login, password)
                    if employee is not None:
                        self.is_login = True
                        self.who_login = "Сотрудник"
                        auth_frame.destroy()  # Убираем виджет авторизации
                        # Создаем новый виджет главного окна
                        #main_app = MainAppFrame(root, self.who_login)
                        #main_app.pack(padx=20, pady=20, fill="both", expand=True)
                        return True
                    else:
                        return False
                if role == "Пользователь":
                    client = client_controller.authenticate(login, password)
                    if client is not None:
                        self.is_login = True
                        self.who_login = "Пользователь"
                        auth_frame.destroy()  # Убираем виджет авторизации
                        # Создаем новый виджет главного окна
                        main_app = UserFrame(root, session, client)
                        main_app.pack(padx=20, pady=20, fill="both", expand=True)
                        return True
                    else:
                        return False
            except Exception as e:
                logging.error(e)
                CTkMessagebox(title="Error", icon="cancel", message=str(e))
                return False

        def registration_callback(registration_data, role):
            if role == "Пользователь":
                try:
                    client = client_controller.create_client(registration_data)
                    if client is not None:
                        logging.info("Регистрация прошла успешно")
                        return True
                    else:
                        logging.error("Регистрация прошла с ошибкой")
                        return False
                except Exception as e:
                    logging.error(e)
                    CTkMessagebox(title="Error", icon="cancel", message=str(e))
                    return False

        root = ctk.CTk()
        root.geometry("500x600")
        root.title("Аутентификация")

        # Создаем виджет авторизации
        auth_frame = AuthFrame(root, login_callback=login_callback,
                               registration_callback=registration_callback)
        auth_frame.pack(padx=20, pady=20, fill="both", expand=True)

        root.mainloop()


if __name__ == "__main__":
    main_window = main_window()