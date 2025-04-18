import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget,
    QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableView, QMessageBox, QCheckBox,
    QFormLayout, QComboBox, QDateEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QStandardItemModel, QStandardItem
from datetime import datetime
from controllers.EmployeeController import EmployeeController
from controllers.MedicineController import MedicineController
from controllers.OrderController import OrderController
from controllers.SupplierController import SupplierController
from controllers.ShipmentController import ShipmentController
from controllers.ShipmentItemController import ShipmentItemController
from models.base import session


class LoginDialog(QDialog):
    def __init__(self, employee_ctrl):
        super().__init__()
        self.employee_ctrl = employee_ctrl
        self.setWindowTitle("Вход")
        self.setMinimumSize(300, 150)

        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.show_pass_cb = QCheckBox("Показать пароль")
        self.show_pass_cb.stateChanged.connect(self.toggle_password)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.handle_login)
        register_btn = QPushButton("Регистрация")
        register_btn.clicked.connect(self.open_register)

        form = QFormLayout()
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow(self.show_pass_cb)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def toggle_password(self, state):
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        user = self.employee_ctrl.authenticate(login, password)
        if user:
            self.accept()
            self.user = user
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_register(self):
        dlg = RegisterDialog(self.employee_ctrl)
        dlg.exec_()


class RegisterDialog(QDialog):
    def __init__(self, employee_ctrl):
        super().__init__()
        self.employee_ctrl = employee_ctrl
        self.setWindowTitle("Регистрация")
        self.setMinimumSize(400, 350)

        self.fname_input = QLineEdit()
        self.lname_input = QLineEdit()
        fio_regex = QRegExp(r"[А-Яа-яA-Za-z\s-]+")
        fio_validator = QRegExpValidator(fio_regex)
        self.fname_input.setValidator(fio_validator)
        self.lname_input.setValidator(fio_validator)

        self.position_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("00000000000")

        self.dtb_input = QDateEdit()
        self.dtb_input.setCalendarPopup(True)
        self.dtb_input.setDisplayFormat("dd.MM.yyyy")
        self.dtb_input.setDate(QDate.currentDate())

        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.show_pass_cb = QCheckBox("Показать пароль")
        self.show_pass_cb.stateChanged.connect(
            lambda s: self.password_input.setEchoMode(
                QLineEdit.Normal if s == Qt.Checked else QLineEdit.Password
            )
        )
        self.admin_cb = QCheckBox("Администратор")

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.handle_register)

        form = QFormLayout()
        form.addRow("Имя:", self.fname_input)
        form.addRow("Фамилия:", self.lname_input)
        form.addRow("Должность:", self.position_input)
        form.addRow("Телефон (11 цифр):", self.phone_input)
        form.addRow("Дата рождения:", self.dtb_input)
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow(self.show_pass_cb)
        form.addRow(self.admin_cb)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(register_btn)
        self.setLayout(layout)

    def handle_register(self):
        data = {
            'FName': self.fname_input.text(),
            'LName': self.lname_input.text(),
            'Position': self.position_input.text(),
            'Number': self.phone_input.text(),
            'DTB': self.dtb_input.date().toString("yyyy-MM-dd"),
            'Login': self.login_input.text(),
            'Pass': self.password_input.text(),
            'Admin': self.admin_cb.isChecked()
        }
        try:
            self.employee_ctrl.create_employee(data)
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))


class EditRecordDialog(QDialog):
    def __init__(self, data, title, is_edit=True):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)

        self.is_edit = is_edit
        self.data = data

        self.fname_input = QLineEdit(self.data.get('FName', ''))
        self.lname_input = QLineEdit(self.data.get('LName', ''))
        self.position_input = QLineEdit(self.data.get('Position', ''))
        self.phone_input = QLineEdit(self.data.get('Number', ''))
        self.phone_input.setInputMask("00000000000")

        self.dtb_input = QDateEdit()
        self.dtb_input.setCalendarPopup(True)
        self.dtb_input.setDisplayFormat("dd.MM.yyyy")
        self.dtb_input.setDate(QDate.fromString(self.data.get('DTB', ''), "yyyy-MM-dd"))

        self.login_input = QLineEdit(self.data.get('Login', ''))
        self.password_input = QLineEdit(self.data.get('Pass', ''))
        self.password_input.setEchoMode(QLineEdit.Password)

        self.admin_cb = QCheckBox("Администратор")
        self.admin_cb.setChecked(self.data.get('Admin', False))

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)

        form = QFormLayout()
        form.addRow("Имя:", self.fname_input)
        form.addRow("Фамилия:", self.lname_input)
        form.addRow("Должность:", self.position_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Дата рождения:", self.dtb_input)
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow(self.admin_cb)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_data(self):
        data = {
            'FName': self.fname_input.text(),
            'LName': self.lname_input.text(),
            'Position': self.position_input.text(),
            'Number': self.phone_input.text(),
            'DTB': self.dtb_input.date().toString("yyyy-MM-dd"),
            'Login': self.login_input.text(),
            'Pass': self.password_input.text(),
            'Admin': self.admin_cb.isChecked()
        }
        self.accept()


class AddRecordDialog(EditRecordDialog):
    def __init__(self, title):
        super().__init__({}, title, is_edit=False)


class MainWindow(QMainWindow):
    def __init__(self, controllers, user):
        super().__init__()
        self.controllers = controllers
        self.user = user
        self.setWindowTitle("Система управления аптекой")
        self.resize(1100, 650)

        tabs = QTabWidget()

        tabs.addTab(self.create_table_tab(
            self.controllers['employee'],
            ['id', 'FName', 'LName', 'Position', 'Number', 'Login', 'DTB', 'Admin'],
            "Сотрудники",
            user.Admin,
            is_employee=True
        ), "Сотрудники")

        tabs.addTab(self.create_table_tab(
            self.controllers['medicine'],
            ['id', 'MName', 'Price', 'Count', 'Description', 'Category', 'BT', 'Supplier'],
            "Лекарства",
            user.Admin
        ), "Лекарства")

        tabs.addTab(self.create_table_tab(
            self.controllers['order'],
            ['id', 'DateReg', 'Amount', 'Status', 'Employee', 'Medicine'],
            "Заказы",
            user.Admin
        ), "Заказы")

        tabs.addTab(self.create_table_tab(
            self.controllers['supplier'],
            ['id', 'CompName', 'Address', 'Number', 'INN'],
            "Поставщики",
            user.Admin
        ), "Поставщики")

        tabs.addTab(self.create_table_tab(
            self.controllers['shipment'],
            ['id', 'Supplier', 'DateReg', 'Amount', 'Status', 'Employee'],
            "Поставки",
            user.Admin
        ), "Поставки")

        tabs.addTab(self.create_table_tab(
            self.controllers['shipmentitem'],
            ['id', 'Shipment', 'Medicine', 'Quantity'],
            "Позиции поставок",
            user.Admin
        ), "Позиции поставок")

        self.setCentralWidget(tabs)

    def create_table_tab(self, ctrl, fields, title, is_admin, is_employee=False):
        widget = QWidget()
        vbox = QVBoxLayout()

        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск...")
        vbox.addWidget(search_input)

        model = QStandardItemModel()
        headers = []
        rus_map = {
            'id': 'Номер ПП', 'FName': 'Имя', 'LName': 'Фамилия', 'Position': 'Должность',
            'Number': 'Телефон', 'Login': 'Логин', 'DTB': 'Дата рождения', 'Admin': 'Админ',
            'MName': 'Название', 'Price': 'Цена', 'Count': 'Остаток', 'Description': 'Описание',
            'Category': 'Категория', 'BT': 'BT', 'Supplier': 'Поставщик',
            'DateReg': 'Дата', 'Amount': 'Количество', 'Status': 'Статус',
            'Employee': 'Сотрудник', 'Medicine': 'Лекарство',
            'CompName': 'Компания', 'Address': 'Адрес', 'INN': 'ИНН',
            'Shipment': 'Поставка', 'Quantity': 'Количество'
        }
        for f in fields:
            headers.append(rus_map.get(f, f))
        model.setHorizontalHeaderLabels(headers)

        for row in ctrl.get_all():
            items = []
            for f in fields:
                val = getattr(row, f) if hasattr(row, f) else row[fields.index(f)]
                items.append(QStandardItem(str(val)))
            model.appendRow(items)

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(-1)
        table = QTableView()
        table.setModel(proxy)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.resizeColumnsToContents()
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        search_input.textChanged.connect(
            lambda text: proxy.setFilterRegExp(
                QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString)
            )
        )

        if not is_admin or is_employee:
            table.setEditTriggers(QTableView.NoEditTriggers)

        vbox.addWidget(table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        edit_btn = QPushButton("Редактировать")
        del_btn = QPushButton("Удалить")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        vbox.addLayout(btn_layout)

        if not is_admin:
            add_btn.setEnabled(False)
            del_btn.setEnabled(False)

        edit_btn.clicked.connect(lambda: self.handle_edit(title))
        add_btn.clicked.connect(lambda: self.handle_add(title))

        widget.setLayout(vbox)
        return widget

    def handle_add(self, title):
        if title == "Сотрудники":
            dlg = AddRecordDialog("Добавить сотрудника")
        elif title == "Лекарства":
            dlg = AddRecordDialog("Добавить лекарство")
        else:
            dlg = AddRecordDialog(f"Добавить запись в {title}")

        dlg.exec_()

    def handle_edit(self, title):
        test_data={}
        if title == "Сотрудники":
            dlg = EditRecordDialog(test_data, "Редактировать сотрудника")
        elif title == "Лекарства":
            dlg = EditRecordDialog(test_data, "Редактировать лекарство")
        else:
            dlg = EditRecordDialog(test_data, f"Редактировать запись в {title}")

        dlg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    employee_ctrl = EmployeeController(session)
    medicine_ctrl = MedicineController(session)
    order_ctrl = OrderController(session)
    supplier_ctrl = SupplierController(session)
    shipment_ctrl = ShipmentController(session)
    shipment_item_ctrl = ShipmentItemController(session)

    login = LoginDialog(employee_ctrl)
    if login.exec_() == QDialog.Accepted:
        user = login.user
        controllers = {
            'employee': employee_ctrl,
            'medicine': medicine_ctrl,
            'order': order_ctrl,
            'supplier': supplier_ctrl,
            'shipment': shipment_ctrl,
            'shipmentitem': shipment_item_ctrl
        }
        main_win = MainWindow(controllers, user)
        main_win.show()
        sys.exit(app.exec_())
