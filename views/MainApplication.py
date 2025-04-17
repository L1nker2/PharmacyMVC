import customtkinter as ctk
from views.OrderView import OrderView
from views.EmployeeView import EmployeesView
from views.MedicineView import MedicineView
from views.customUI.LoginWindow import LoginWindow
from models.base import session
from controllers.OrderController import OrderController
from controllers.EmployeeController import EmployeeController
from controllers.MedicineController import MedicineController
from models.employee import Employee
from models.shipment import Shipment
from models.medicine import Medicine
from models.order import Order
from models.shipment_item import ShipmentItem
from models.supplier import Supplier

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTk):
    def __init__(self, controllers=None):
        super().__init__()
        self.controllers = controllers or {}
        # Скрываем главное окно до успешного логина
        self.withdraw()
        self.title("Основное приложение")
        self.geometry("1024x768")

        # Сразу открываем окно логина
        LoginWindow(master=self, controller=self.controllers.get("employees"))

        # Меню вкладок
        tab_frame = ctk.CTkFrame(self)
        tab_frame.pack(side="top", fill="x")
        self.tab_buttons = {}
        tabs = [("Продажи", self.show_sales), ("Сотрудники", self.show_employees), ("Медикаменты", self.show_medications)]
        for name, cmd in tabs:
            btn = ctk.CTkButton(tab_frame, text=name, command=cmd, width=120)
            btn.pack(side="left", padx=5, pady=5)
            self.tab_buttons[name] = btn

        # Контейнер для представлений
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Инициализация представлений
        self.views = {
            "Продажи": OrderView(self.container, controller=self.controllers.get("sales")),
            "Сотрудники": EmployeesView(self.container, controller=self.controllers.get("employees")),
            "Медикаменты": MedicineView(self.container, controller=self.controllers.get("medications")),
        }
        for view in self.views.values():
            view.place(relwidth=1, relheight=1)
            view.lower()

        # Показ по умолчанию (после логина)
        self.show_sales()

    def show_view(self, name):
        for tab_name, btn in self.tab_buttons.items():
            btn.configure(fg_color="transparent")
        self.tab_buttons[name].configure(fg_color="purple")
        self.views[name].lift()

    def show_sales(self):
        self.show_view("Продажи")

    def show_employees(self):
        self.show_view("Сотрудники")

    def show_medications(self):
        self.show_view("Медикаменты")

if __name__ == "__main__":
    order_controller = OrderController(session)
    employee_controller = EmployeeController(session)
    medicine_controller = MedicineController(session)
    controllers = {'sales': order_controller, 'employees': employee_controller, 'medications': medicine_controller}
    app = MainApplication(controllers)
    app.mainloop()