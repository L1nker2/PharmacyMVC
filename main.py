import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableView, QMessageBox, QCheckBox,
    QFormLayout, QDateEdit, QSizePolicy,
    QAbstractItemView, QComboBox
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QStandardItemModel, QStandardItem
from controllers.EmployeeController import EmployeeController
from controllers.MedicineController import MedicineController
from controllers.OrderController import OrderController
from controllers.SupplierController import SupplierController
from controllers.ShipmentController import ShipmentController
from controllers.ShipmentItemController import ShipmentItemController
from models.base import session
from models.base import BaseModel
from core.security import Security

#region LoginDialog
# noinspection PyUnresolvedReferences
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
#endregion

#region RegisterDialog
# noinspection PyUnresolvedReferences
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
        #self.admin_cb = QCheckBox("Администратор")

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
        #form.addRow(self.admin_cb)

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
            'Admin': False
        }
        try:
            self.employee_ctrl.create_employee(data)
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
#endregion

#region EditEmployee
# noinspection PyUnresolvedReferences
class EmployeeEditRecordDialog(QDialog):
    def __init__(self, data, title, controller, ):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)
        self.ctrl = controller
        self.employee = self.ctrl.get_employee_by_id(data[0])
        self.data = data or []  # Защита от None
        self.record_id = data[0] if data and len(data) > 0 else None  # Сохраняем ID записи

        layout = QVBoxLayout()
        form = QFormLayout()

        # Создаем поля формы
        self.fname_input = QLineEdit(self.employee.FName)
        self.lname_input = QLineEdit(self.employee.LName)
        self.position_input = QLineEdit(self.employee.Position)

        self.phone_input = QLineEdit(self.employee.Number)
        self.phone_input.setInputMask("00000000000")

        self.dtb_input = QDateEdit()
        self.dtb_input.setCalendarPopup(True)
        self.dtb_input.setDisplayFormat("dd.MM.yyyy")
        self.dtb_input.setDate(QDate.fromString(str(self.employee.DTB)))

        self.login_input = QLineEdit(self.employee.Login)
        self.password_input = QLineEdit(Security.decrypt_password(self.employee.Pass))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.show_pass_cb = QCheckBox("Показать пароль")
        self.show_pass_cb.stateChanged.connect(self.toggle_password)

        self.admin_cb = QCheckBox("Администратор")
        self.admin_cb.setChecked(bool(self.employee.Admin))

        # Добавляем поля в форму
        form.addRow("Имя:", self.fname_input)
        form.addRow("Фамилия:", self.lname_input)
        form.addRow("Должность:", self.position_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Дата рождения:", self.dtb_input)
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow(self.show_pass_cb)
        form.addRow(self.admin_cb)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_data(self):
        """Собирает данные из формы и закрывает диалог"""
        try:
            self.result_data = {
                'id': self.record_id,  # Добавляем ID записи
                'FName': self.fname_input.text(),
                'LName': self.lname_input.text(),
                'Position': self.position_input.text(),
                'Number': self.phone_input.text(),
                'DTB': self.dtb_input.date().toString("yyyy-MM-dd"),
                'Login': self.login_input.text(),
                'Pass': self.password_input.text() if self.password_input.text() else None,
                'Admin': self.admin_cb.isChecked()
            }
            self.ctrl.update_employee(self.record_id, self.result_data)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, title="Ошибка", text=f"При изменении произошла ошибка:\n{e}")
        self.accept()

    def toggle_password(self, state):
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
#endregion

#region AddEmployee
# noinspection PyUnresolvedReferences
class EmployeeAddRecordDialog(QDialog):
    def __init__(self, title, controller):
        super().__init__()
        self.ctrl = controller

        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Создаем поля формы
        self.fname_input = QLineEdit("")
        self.lname_input = QLineEdit("")
        self.position_input = QLineEdit("")

        self.phone_input = QLineEdit("")
        self.phone_input.setInputMask("00000000000")

        self.dtb_input = QDateEdit()
        self.dtb_input.setDate(QDate.currentDate())
        self.dtb_input.setCalendarPopup(True)
        self.dtb_input.setDisplayFormat("dd.MM.yyyy")
        self.dtb_input.setDate(QDate.currentDate())

        self.login_input = QLineEdit("")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.admin_cb = QCheckBox("Администратор")
        self.admin_cb.setChecked(False)

        # Добавляем поля в форму
        form.addRow("Имя:", self.fname_input)
        form.addRow("Фамилия:", self.lname_input)
        form.addRow("Должность:", self.position_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Дата рождения:", self.dtb_input)
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow(self.admin_cb)

        save_btn = QPushButton("Добавить")
        save_btn.clicked.connect(self.add_employee)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def add_employee(self):
        """Собирает данные из формы и закрывает диалог"""
        try:
            result_data = {
                'FName': self.fname_input.text(),
                'LName': self.lname_input.text(),
                'Position': self.position_input.text(),
                'Number': self.phone_input.text(),
                'DTB': self.dtb_input.date().toString("yyyy-MM-dd"),
                'Login': self.login_input.text(),
                'Pass': self.password_input.text() if self.password_input.text() else None,
                'Admin': self.admin_cb.isChecked()
            }
            self.ctrl.create_employee(result_data)
        except Exception as e:
            QMessageBox.critical(self, title="Ошибка", text=f"При добавлении произошла ошибка:\n{e}")
            pass
        self.accept()
#endregion

#region EditSupplier
# noinspection PyUnresolvedReferences
class SupplierEditRecordDialog(QDialog):
    def __init__(self, data, title, controller, ):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)
        self.ctrl = controller
        self.supplier = self.ctrl.get_supplier_by_id(data[0])
        self.data = data or []  # Защита от None
        self.record_id = data[0] if data and len(data) > 0 else None  # Сохраняем ID записи

        layout = QVBoxLayout()
        form = QFormLayout()

        # Создаем поля формы
        self.compname_input = QLineEdit(self.supplier.CompName)
        self.adress_input = QLineEdit(self.supplier.Address)
        self.number_input = QLineEdit(self.supplier.Number)
        self.number_input.setInputMask("00000000000")
        self.inn_input = QLineEdit(self.supplier.INN)

        # Добавляем поля в форму
        form.addRow("Название:", self.compname_input)
        form.addRow("Адресс:", self.adress_input)
        form.addRow("Телефон:", self.number_input)
        form.addRow("Инн:", self.inn_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_data(self):
        """Собирает данные из формы и закрывает диалог"""
        try:
            self.result_data = {
                'id': self.record_id,  # Добавляем ID записи
                'CompName': self.compname_input.text(),
                'Address': self.adress_input.text(),
                'Number': self.number_input.text(),
                'INN': self.inn_input.text(),
            }
            self.ctrl.update_supplier(self.record_id, self.result_data)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, title="Ошибка", text=f"При изменении произошла ошибка:\n{e}")
        self.accept()
#endregion

#region AddSupplier
# noinspection PyUnresolvedReferences
class SupplierAddRecordDialog(QDialog):
    def __init__(self, title, controller):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)
        self.ctrl = controller

        layout = QVBoxLayout()
        form = QFormLayout()

        # Создаем поля формы
        self.compname_input = QLineEdit()
        self.adress_input = QLineEdit()
        self.number_input = QLineEdit()
        self.number_input.setInputMask("00000000000")
        self.inn_input = QLineEdit()

        # Добавляем поля в форму
        form.addRow("Название:", self.compname_input)
        form.addRow("Адресс:", self.adress_input)
        form.addRow("Телефон:", self.number_input)
        form.addRow("Инн:", self.inn_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)

        layout.addLayout(form)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_data(self):
        """Собирает данные из формы и закрывает диалог"""
        try:
            self.result_data = {
                'CompName': self.compname_input.text(),
                'Address': self.adress_input.text(),
                'Number': self.number_input.text(),
                'INN': self.inn_input.text(),
            }
            self.ctrl.create_supplier(self.result_data)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, title="Ошибка", text=f"При изменении произошла ошибка:\n{e}")
        self.accept()
#endregion

#region AddShipment
# noinspection PyUnresolvedReferences
class ShipmentAddRecordDialog(QDialog):
    def __init__(self, title, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle(title)
        self.setMinimumSize(400, 350)

        # Основной layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 1. Выпадающий список поставщиков
        self.supplier_combo = QComboBox()
        suppliers = self.controller.get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.CompName, supplier.id)
        form_layout.addRow("Поставщик:", self.supplier_combo)

        # 2. Выпадающий список сотрудников
        self.employee_combo = QComboBox()
        employees = self.controller.get_all_employees()
        for employee in employees:
            self.employee_combo.addItem(f"{employee.LName} {employee.FName}", employee.id)
        form_layout.addRow("Сотрудник:", self.employee_combo)

        # 3. Поля даты и статуса
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата поставки:", self.date_edit)

        self.status_check = QCheckBox("Активна")
        self.status_check.setChecked(True)
        form_layout.addRow("Статус:", self.status_check)

        # 4. Кнопка сохранения
        self.save_btn = QPushButton("Сохранить поставку")
        self.save_btn.clicked.connect(self.save_shipment)

        # Сборка интерфейса
        layout.addLayout(form_layout)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        self.setWindowTitle("Новая поставка")

    def save_shipment(self):
        data={
            "DateReg": self.date_edit.date().toPyDate(),
            "Status": self.status_check.isChecked(),
            "Supplier": self.supplier_combo.currentData(),
            "Employee": self.employee_combo.currentData(),
            "Price": 0  # Будет рассчитано автоматически в контроллере
        }
        print(data)
        items = 0
        self.accept()
#endregion


# noinspection PyUnresolvedReferences
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
            ['id', 'Supplier', 'DateReg', 'Price', 'Status', 'Employee'],
            "Поставки",
            user.Admin
        ), "Поставки")

        self.setCentralWidget(tabs)

    def refresh_current_tab(self):
        """Обновляет текущую активную вкладку"""
        tab_widget = self.centralWidget()
        current_idx = tab_widget.currentIndex()
        title = tab_widget.tabText(current_idx)

        # Определяем параметры для каждой вкладки
        if title == "Сотрудники":
            tab_widget.removeTab(current_idx)
            tab_widget.insertTab(current_idx,
                                 self.create_table_tab(
                                     self.controllers['employee'],
                                     ['id', 'FName', 'LName', 'Position', 'Number', 'Login', 'DTB', 'Admin'],
                                     "Сотрудники",
                                     self.user.Admin,
                                     is_employee=True
                                 ), "Сотрудники")

        elif title == "Лекарства":
            tab_widget.removeTab(current_idx)
            tab_widget.insertTab(current_idx,
                                 self.create_table_tab(
                                     self.controllers['medicine'],
                                     ['id', 'MName', 'Price', 'Count', 'Description', 'Category', 'BT', 'Supplier'],
                                     "Лекарства",
                                     self.user.Admin
                                 ), "Лекарства")

        elif title == "Заказы":
            tab_widget.removeTab(current_idx)
            tab_widget.insertTab(current_idx,
                                 self.create_table_tab(
                                    self.controllers['order'],
                                    ['id', 'DateReg', 'Amount', 'Status', 'Employee', 'Medicine'],
                                    "Заказы",
                                    user.Admin
                                ), "Заказы")

        elif title == "Поставщики":
            tab_widget.removeTab(current_idx)
            tab_widget.insertTab(current_idx,
                                 self.create_table_tab(
                                     self.controllers['supplier'],
                                     ['id', 'CompName', 'Address', 'Number', 'INN'],
                                     "Поставщики",
                                     user.Admin
                                 ), "Поставщики")

        elif title == "Поставки":
            tab_widget.removeTab(current_idx)
            tab_widget.insertTab(current_idx,
                                 self.create_table_tab(
                                     self.controllers['shipment'],
                                     ['id', 'Supplier', 'DateReg', 'Price', 'Status', 'Employee'],
                                     "Поставки",
                                     user.Admin
                                 ), "Поставки")


        tab_widget.setCurrentIndex(current_idx)

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
            'DateReg': 'Дата', 'Status': 'Статус',
            'Employee': 'Сотрудник', 'Medicine': 'Лекарство',
            'CompName': 'Компания', 'Address': 'Адрес', 'INN': 'ИНН',
            'Shipment': 'Поставка', 'Quantity': 'Количество'
        }
        for f in fields:
            headers.append(rus_map.get(f, f))
        model.setHorizontalHeaderLabels(headers)
        rows = ctrl.get_all()
        for row in rows:
            items = []
            for f in fields:
                if not hasattr(row, f):
                    print(f"Предупреждение: атрибут {f} не найден в объекте Shipment")
                # Получаем значение атрибута
                val = getattr(row, f)
                items.append(QStandardItem(str(val)))
            model.appendRow(items)
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(-1)
        table = QTableView()
        table.setModel(proxy)
        table.sortByColumn(0, Qt.AscendingOrder)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.resizeColumnsToContents()
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

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

        if not is_admin and title== "Сотрудники":
            add_btn.setEnabled(False)
            del_btn.setEnabled(False)

        # здесь нужно получить переменную выделенной строки
        def get_selected_row():
            selected_indexes = table.selectionModel().selectedRows()
            if selected_indexes:
                # Получаем первую выделенную строку (если разрешено множественное выделение)
                selected_row = selected_indexes[0].row()
                # Получаем данные через proxy model
                return [
                    proxy.data(proxy.index(selected_row, col))
                    for col in range(proxy.columnCount())
                ]
            return None

        edit_btn.clicked.connect(lambda: self.handle_edit(title, get_selected_row()))
        add_btn.clicked.connect(lambda: self.handle_add(title))
        del_btn.clicked.connect(lambda: self.handle_delete(title, get_selected_row()))

        widget.setLayout(vbox)
        return widget

    def handle_add(self, title):
        if title == "Сотрудники":
            dlg = EmployeeAddRecordDialog(title="Добавить сотрудника", controller=self.controllers['employee'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Лекарства":
            pass
            #dlg = AddRecordDialog("Добавить лекарство")
        elif title == "Заказы":
            pass
        elif title == "Поставщики":
            dlg = SupplierAddRecordDialog(title="Добавить поставщика", controller=self.controllers['supplier'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Поставки":
            dlg = ShipmentAddRecordDialog(title="Добавить поставку", controller=self.controllers['shipment'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()

    def handle_edit(self, title, data):
        if not data:
            QMessageBox.warning(self, "Ошибка", "Не выбрана запись для редактирования")
            return

        if title == "Сотрудники":
            dlg = EmployeeEditRecordDialog(data=data, title="Редактировать сотрудника",
                                           controller=self.controllers['employee'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Лекарства":
            pass
            #dlg = EditRecordDialog(test_data, "Редактировать лекарство", controller=self.controllers['employee'])
        elif title == "Заказы":
            pass
            #dlg = EditRecordDialog(test_data, f"Редактировать запись в {title}", controller=self.controllers['employee'])
        elif title == "Поставщики":
            dlg = SupplierEditRecordDialog(title="Редактировать поставщика", data=data,
                                           controller = self.controllers['supplier'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Поставки":
            pass

    def handle_delete(self, title, data):
        if not data:
            QMessageBox.warning(self, "Ошибка", "Не выбрана запись для редактирования")
            return


        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Подтверждение удаления")
        msg.setText(f"Вы уверены, что хотите удалить запись из {title}?\n"
                    f"Это повлечет за собой удаление всех связанных с записей!")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Показываем диалог и ждем ответа
        answer = msg.exec_()

        if answer == QMessageBox.Yes:
            try:
                if title == "Сотрудники":
                    self.controllers['employee'].delete_employee(data[0])
                elif title == "Лекарства":
                    pass
                    #self.controllers['medicine'].delete_medicine(data[0])
                # Добавьте обработку для других вкладок

                # Обновляем таблицу
                self.refresh_current_tab()
                QMessageBox.information(self, "Успех", "Запись успешно удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {str(e)}")







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
