import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableView, QMessageBox, QCheckBox,
    QFormLayout, QDateEdit, QSizePolicy, QHeaderView,
    QAbstractItemView, QComboBox, QLabel, QTableWidget,
    QSpinBox, QTableWidgetItem, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QStandardItemModel, QStandardItem, QIntValidator, QColor, QBrush
from controllers.EmployeeController import EmployeeController
from controllers.MedicineController import MedicineController
from controllers.OrderController import OrderController
from controllers.SupplierController import SupplierController
from controllers.ShipmentController import ShipmentController
from controllers.ShipmentItemController import ShipmentItemController
from models.base import session
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
    def __init__(self, title, controllers):
        super().__init__()
        self.medicine_controller = controllers['medicine']
        self.employee_controller = controllers['employee']
        self.suppliers_controller = controllers['supplier']
        self.shipment_controller = controllers['shipment']

        self.selected_medicines = []  # Список выбранных медикаментов

        self.setWindowTitle(title)
        self.setMinimumSize(1000, 600)  # Увеличиваем размер окна

        # Основной layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 1. Выпадающий список поставщиков
        self.supplier_combo = QComboBox()
        suppliers = self.suppliers_controller.get_all()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.CompName, supplier.id)
        form_layout.addRow("Поставщик:", self.supplier_combo)
        self.supplier_combo.currentIndexChanged.connect(self.update_medicines_table)

        # 2. Выпадающий список сотрудников
        self.employee_combo = QComboBox()
        employees = self.employee_controller.get_all()
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

        # 4. Таблица доступных медикаментов
        self.medicines_label = QLabel("Доступные медикаменты:")
        self.medicines_table = QTableWidget()
        self.medicines_table.setColumnCount(5)
        self.medicines_table.setHorizontalHeaderLabels(["Выбрать", "Название", "Описание", "Цена", "Количество"])
        self.medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.medicines_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.medicines_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 5. Поля для работы с медикаментами
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(1000)
        self.quantity_spin.setValue(1)

        self.add_meds_btn = QPushButton("Добавить выбранные")
        self.add_meds_btn.clicked.connect(self.add_selected_medicines)

        # 6. Таблица выбранных медикаментов
        self.selected_meds_label = QLabel("Выбранные медикаменты:")
        self.selected_meds_table = QTableWidget()
        self.selected_meds_table.setColumnCount(5)
        self.selected_meds_table.setHorizontalHeaderLabels(["ID", "Название", "Количество", "Цена", "Сумма"])
        self.selected_meds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 7. Кнопка удаления выбранных медикаментов
        self.remove_meds_btn = QPushButton("Удалить выбранные")
        self.remove_meds_btn.clicked.connect(self.remove_selected_medicines)

        # 8. Кнопка сохранения
        self.save_btn = QPushButton("Сохранить поставку")
        self.save_btn.clicked.connect(self.save_shipment)

        # Сборка интерфейса
        layout.addLayout(form_layout)
        layout.addWidget(self.medicines_label)
        layout.addWidget(self.medicines_table)
        layout.addWidget(QLabel("Количество:"))
        layout.addWidget(self.quantity_spin)
        layout.addWidget(self.add_meds_btn)
        layout.addWidget(self.selected_meds_label)
        layout.addWidget(self.selected_meds_table)
        layout.addWidget(self.remove_meds_btn)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        # Инициализация таблицы медикаментов
        self.update_medicines_table()

    def update_medicines_table(self):
        """Обновляет таблицу доступных медикаментов при изменении поставщика"""
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            return

        # Получаем медикаменты и гарантируем, что это список
        Medicine = self.medicine_controller.get_medicines_by_supplier(supplier_id)
        medicines = Medicine
        row_cout = len(medicines)

        if not medicines:
            # Если медикаментов нет, показываем сообщение
            self.medicines_table.setRowCount(1)

            # Очищаем все ячейки
            for col in range(self.medicines_table.columnCount()):
                self.medicines_table.setItem(0, col, QTableWidgetItem(""))

            # Делаем объединенную ячейку с сообщением
            self.medicines_table.setSpan(0, 0, 1, self.medicines_table.columnCount())
            self.medicines_table.setItem(0, 0, QTableWidgetItem("Медикаменты отсутствуют"))
            self.medicines_table.item(0, 0).setTextAlignment(Qt.AlignCenter)

            # Делаем текст серым и курсивом
            font = self.medicines_table.item(0, 0).font()
            font.setItalic(True)
            self.medicines_table.item(0, 0).setFont(font)
            self.medicines_table.item(0, 0).setForeground(Qt.gray)

            # Отключаем чекбокс (если он есть)
            if self.medicines_table.cellWidget(0, 0):
                self.medicines_table.cellWidget(0, 0).layout().itemAt(0).widget().setEnabled(False)

            return

        # Если медикаменты есть, отображаем их
        self.medicines_table.setRowCount(len(medicines))
        self.medicines_table.clearSpans()  # Сбрасываем объединенные ячейки

        for row, medicine in enumerate(medicines):
            # Колонка с чекбоксом
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            checkbox = QCheckBox()
            chk_layout.addWidget(checkbox)
            self.medicines_table.setCellWidget(row, 0, chk_widget)

            # Остальные колонки
            self.medicines_table.setItem(row, 1, QTableWidgetItem(medicine.MName))
            self.medicines_table.setItem(row, 2, QTableWidgetItem(medicine.Description))
            self.medicines_table.setItem(row, 3, QTableWidgetItem(str(medicine.Price)))
            self.medicines_table.setItem(row, 4, QTableWidgetItem(str(medicine.Count)))

    def add_selected_medicines(self):
        """Добавляет выбранные медикаменты в список"""
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            return

        count = self.quantity_spin.value()

        # Получаем все медикаменты поставщика один раз
        medicine = self.medicine_controller.get_medicines_by_supplier(supplier_id)
        medicines = [medicine] if medicine else []

        for row in range(self.medicines_table.rowCount()):
            widget = self.medicines_table.cellWidget(row, 0)
            checkbox = widget.layout().itemAt(0).widget()

            if checkbox.isChecked() and row < len(medicines):
                med = medicines[row]
                med_id = med.id
                name = self.medicines_table.item(row, 1).text()
                price = float(self.medicines_table.item(row, 3).text())
                total = price * count

                # Проверяем, не добавлен ли уже этот медикамент
                existing_idx = next((i for i, m in enumerate(self.selected_medicines)
                                     if m["id"] == med_id), None)

                if existing_idx is not None:
                    # Увеличиваем количество, если уже добавлен
                    self.selected_medicines[existing_idx]["Count"] += count
                    self.selected_medicines[existing_idx]["total"] += total
                else:
                    # Добавляем новый медикамент
                    self.selected_medicines.append({
                        "id": med_id,
                        "name": name,
                        "Count": count,
                        "Price": price,
                        "total": total
                    })

        self.update_selected_medicines_table()

    def remove_selected_medicines(self):
        """Удаляет выбранные медикаменты из списка"""
        selected_rows = set(index.row() for index in
                            self.selected_meds_table.selectedIndexes())

        # Удаляем в обратном порядке, чтобы не сбить индексы
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self.selected_medicines):
                self.selected_medicines.pop(row)

        self.update_selected_medicines_table()

    def update_selected_medicines_table(self):
        """Обновляет таблицу выбранных медикаментов"""
        self.selected_meds_table.setRowCount(len(self.selected_medicines))

        for row, med in enumerate(self.selected_medicines):
            self.selected_meds_table.setItem(row, 0, QTableWidgetItem(str(med["id"])))
            self.selected_meds_table.setItem(row, 1, QTableWidgetItem(med["name"]))
            self.selected_meds_table.setItem(row, 2, QTableWidgetItem(str(med["Count"])))
            self.selected_meds_table.setItem(row, 3, QTableWidgetItem(str(med["Price"])))
            self.selected_meds_table.setItem(row, 4, QTableWidgetItem(str(med["total"])))

    def save_shipment(self):
        """Сохраняет поставку с выбранными медикаментами"""
        if not self.selected_medicines:
            #self.controller.show_error_message("Не выбраны медикаменты для поставки")
            return

        # Основные данные поставки
        shipment_data = {
            "DateReg": self.date_edit.date().toPyDate(),
            "Status": self.status_check.isChecked(),
            "Supplier": self.supplier_combo.currentData(),
            "Employee": self.employee_combo.currentData(),
            "Price": sum(med["total"] for med in self.selected_medicines)
        }

        # Список медикаментов
        items = [
            {
                "id": med["id"],
                "Count": med["Count"],  # Используем quantity вместо Count для единообразия
                "Price": med["Price"]
            }
            for med in self.selected_medicines
        ]

        try:
            # Вызываем метод контроллера с разделенными данными
            self.shipment_controller.create_shipment(shipment_data, items)
            self.accept()
        except Exception as e:
            pass
            #self.controller.show_error_message(f"Ошибка при сохранении: {str(e)}")
#endregion

#region AddOrder
# noinspection PyUnresolvedReferences
class OrderAddRecordDialog(QDialog):
    def __init__(self, title, controllers):
        super().__init__()
        self.medicine_controller = controllers['medicine']
        self.employee_controller = controllers['employee']
        self.suppliers_controller = controllers['supplier']
        self.shipment_controller = controllers['shipment']
        self.order_controller = controllers['order']

        self.setWindowTitle(title)

        # Основной layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 1. Поля даты
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Дата поставки:", self.date_edit)

        # 2. Выпадающий список лекарств
        self.medicine_combo = QComboBox()
        medicines = self.medicine_controller.get_all()
        for medicine in medicines:
            self.medicine_combo.addItem(medicine.MName, medicine.id)
        form_layout.addRow("Лекарство:", self.medicine_combo)
        self.medicine_combo.currentIndexChanged.connect(self.update_price)

        # 3. Выпадающий список сотрудников
        self.employee_combo = QComboBox()
        employees = self.employee_controller.get_all()
        for employee in employees:
            self.employee_combo.addItem(f"{employee.LName} {employee.FName}", employee.id)
        form_layout.addRow("Сотрудник:", self.employee_combo)

        # 4. Выбор количества
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(1)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self.edit_price)
        form_layout.addRow("Количество:", self.quantity_spin)

        # 5. Статус заказа
        self.status_check = QCheckBox("Активен")
        self.status_check.setChecked(True)
        form_layout.addRow("Статус:", self.status_check)

        # 6. Метка цены
        self.price_label = QLabel()
        form_layout.addRow("Итоговая цена:", self.price_label)

        # 7. Кнопка сохранения
        self.save_btn = QPushButton("Сохранить сделку")
        self.save_btn.clicked.connect(self.save_order)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def update_price(self):
        medicine_id = self.medicine_combo.currentData()
        if not medicine_id:
            return
        medicine = self.medicine_controller.get_medicine_by_id(medicine_id)

        self.quantity_spin.setMaximum(medicine.Count)
        self.edit_price()

    def edit_price(self):
        medicine_id = self.medicine_combo.currentData()
        if not medicine_id:
            return

        medicine = self.medicine_controller.get_medicine_by_id(medicine_id)
        count = self.quantity_spin.value()

        self.price_label.setText(str(medicine.Price * count))

    def save_order(self):
      """Собирает данные из полей формы и сохраняет заказ через контроллер"""
      try:
        # 1. Собираем данные из полей формы
        order_data = {
          "DateReg": self.date_edit.date().toPyDate(),  # Получаем дату как datetime.date
          "Amount": self.quantity_spin.value(),  # Количество лекарства
          "Status": self.status_check.isChecked(),  # Статус (True/False)
          "Employee": self.employee_combo.currentData(),  # ID сотрудника
          "Medicine": self.medicine_combo.currentData()  # ID лекарства
        }

        # 2. Получаем цену лекарства для расчета суммы
        medicine_id = order_data['Medicine']
        medicine = self.medicine_controller.get_medicine_by_id(medicine_id)
        if not medicine:
          raise ValueError("Лекарство не найдено")

        # 4. Проверяем, что количество не превышает доступное
        if order_data["Amount"] > medicine.Count:
          raise ValueError(f"Недостаточно лекарства на складе. Доступно: {medicine.Count}")

        # 5. Создаем заказ через контроллер
        # (предполагается, что у вас есть метод create_order в order_controller)
        order = self.order_controller.create_order(order_data)

        # 6. Показываем сообщение об успехе и закрываем диалог
        QMessageBox.information(self, "Успех", "Заказ успешно создан!")
        self.accept()

      except ValueError as e:
        # Показываем ошибки валидации
        QMessageBox.warning(self, "Ошибка", str(e))
#endregion

#region AddMedicine
class MedicineAddRecordDialog(QDialog):
    def __init__(self, title, controllers):
        super().__init__()

        self.setWindowTitle(title)

        self.medicine_controller = controllers['medicine']
        self.supplier_controller = controllers['supplier']

        # Основной layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Текстовое поле для названия
        self.mname_input = QLineEdit()
        form_layout.addRow("Название:", self.mname_input)

        # Текстовое поле для цены
        self.price_input = QLineEdit()
        validator = QIntValidator(0, 2147483647)  # Максимальное значение int
        self.price_input.setValidator(validator)
        form_layout.addRow("Цена:", self.price_input)

        # Крутилка для количества(поумолчанию = 0 потому что пополняется через поставки)
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(1)
        self.count_spin.setValue(1)
        form_layout.addRow("Количество:", self.count_spin)

        # Текстовое поле для описания
        self.descriptoin_input = QLineEdit()
        form_layout.addRow("Описание:", self.descriptoin_input)

        # Текстовое поле для категории
        self.category_input = QLineEdit()
        form_layout.addRow("Категория:",self.category_input)

        # Текстовое поле для срока годности
        self.bt_input = QLineEdit()
        form_layout.addRow("Срок годности:", self.bt_input)

        # Выпадающий список для поставщика
        self.supplier_combo = QComboBox()
        suppliers = self.supplier_controller.get_all()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.CompName, supplier.id)
        form_layout.addRow("Поставщик:", self.supplier_combo)

        # Кнопка сохранения
        self.save_btn = QPushButton("Сохранить сделку")
        self.save_btn.clicked.connect(self.save_medicine)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
    
    def save_medicine(self):
        medicine_data = {
            'MName': self.mname_input.text(),
            'Price' : int(self.price_input.text()),
            'Count' : int(self.count_spin.value()),
            'Description' : self.descriptoin_input.text(),
            'Category' : self.category_input.text(),
            'BT' : self.bt_input.text(),
            'Supplier' : self.supplier_combo.currentData()
        }
        try:
            self.medicine_controller.create_medicine(medicine_data)
            QMessageBox.information(self, "Успех", "Медикамент успешно создан!")
            self.accept()
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Ошибка", str(e))

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

        search_button = QPushButton("Найти")
        vbox.addWidget(search_button)

        model = QStandardItemModel()

        headers = []
        rus_map = {
            'id': 'Номер ПП', 'FName': 'Имя', 'LName': 'Фамилия', 'Position': 'Должность',
            'Number': 'Телефон', 'Login': 'Логин', 'DTB': 'Дата рождения', 'Admin': 'Роль',
            'MName': 'Название', 'Price': 'Цена', 'Count': 'Остаток', 'Description': 'Описание',
            'Category': 'Категория', 'BT': 'Срок годности', 'Supplier': 'Поставщик',
            'DateReg': 'Дата', 'Status': 'Статус',
            'Employee': 'Сотрудник', 'Medicine': 'Лекарство',
            'CompName': 'Компания', 'Address': 'Адрес', 'INN': 'ИНН',
            'Shipment': 'Поставка', 'Quantity': 'Количество', 'Amount':'Количество'
        }
        # Маппинг для связанных полей (какое поле отображать вместо ID)
        relation_map = {
            'Employee': {
                'field': 'employee',  # Имя атрибута в модели
                'display': lambda x: f"{x.LName} {x.FName}" if x else ""
            },
            'Supplier': {
                'field': 'supplier',
                'display': lambda x: x.CompName if x else ""
            },
            'Medicine': {
                'field': 'medicine',
                'display': lambda x: x.MName if x else ""
            },
            'Category': {
                'field': 'Category',
                'display': lambda x: x if x else ""
            }
        }
        # Специальное отображение для булевых полей
        bool_display_map = {
            'Status': {True: 'Выполнено', False: 'В ожидании'},
            'Admin': {True: 'Администратор', False: 'Сотрудник'},
            True: 'Да',  # Общее значение для других булевых полей
            False: 'Нет'
        }

        for f in fields:
            headers.append(rus_map.get(f, f))
        model.setHorizontalHeaderLabels(headers)

        rows = ctrl.get_all()
        for row in rows:
            items = []
            for f in fields:
                if not hasattr(row, f):
                    print(f"Предупреждение: атрибут {f} не найден в объекте {type(row).__name__}")
                    items.append(QStandardItem(""))
                    continue

                val = getattr(row, f)

                if f in relation_map:
                    try:
                        # Получаем связанный объект по правильному имени атрибута
                        related_obj = getattr(row, relation_map[f]['field'])
                        display_val = relation_map[f]['display'](related_obj)
                        items.append(QStandardItem(display_val))
                        continue
                    except AttributeError as e:
                        print(f"Ошибка доступа к связанному объекту {f}: {str(e)}")
                        items.append(QStandardItem(""))
                        continue
                    except Exception as e:
                        print(f"Ошибка при обработке связанного поля {f}: {str(e)}")
                        items.append(QStandardItem(""))
                        continue

                # Обработка булевых значений
                if isinstance(val, bool):
                    display_val = bool_display_map.get(f, {}).get(val, bool_display_map.get(val, str(val)))
                    items.append(QStandardItem(display_val))
                    continue

                # Обычное поле
                items.append(QStandardItem(str(val)))

            model.appendRow(items)

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(-1)

        table = QTableView()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setModel(proxy)
        table.setColumnHidden(0, True)
        table.sortByColumn(0, Qt.AscendingOrder)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.resizeColumnsToContents()
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSelectionMode(QAbstractItemView.MultiSelection)


        if title == "Лекарства":
            # Добавляем кнопку фильтрации
            filter_button = QPushButton("Фильтры")
            vbox.addWidget(filter_button)
            
            # Создаем диалог фильтрации
            def show_filter_dialog():
                dialog = QDialog(self)
                dialog.setWindowTitle("Фильтры лекарств")
                layout = QVBoxLayout()
                
                # Фильтр по категории
                category_label = QLabel("Категория:")
                category_combo = QComboBox()
                category_combo.addItem("Все категории", None)
                
                # Получаем уникальные категории из данных
                categories = set()
                for row in range(model.rowCount()):
                    cat_item = model.item(row, fields.index('Category'))
                    if cat_item:
                        categories.add(cat_item.text())
                
                for cat in sorted(categories):
                    category_combo.addItem(cat, cat)
                
                # Фильтр по поставщику
                supplier_label = QLabel("Поставщик:")
                supplier_combo = QComboBox()
                supplier_combo.addItem("Все поставщики", None)
                
                # Получаем уникальных поставщиков из данных
                suppliers = set()
                for row in range(model.rowCount()):
                    sup_item = model.item(row, fields.index('Supplier'))
                    if sup_item:
                        suppliers.add(sup_item.text())
                
                for sup in sorted(suppliers):
                    supplier_combo.addItem(sup, sup)
                
                # Кнопки
                btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                btn_box.accepted.connect(dialog.accept)
                btn_box.rejected.connect(dialog.reject)
                
                # Добавляем элементы в layout
                layout.addWidget(category_label)
                layout.addWidget(category_combo)
                layout.addWidget(supplier_label)
                layout.addWidget(supplier_combo)
                layout.addWidget(btn_box)
                
                dialog.setLayout(layout)
                
                if dialog.exec_() == QDialog.Accepted:
                    # Применяем фильтры
                    category_filter = category_combo.currentData()
                    supplier_filter = supplier_combo.currentData()
                    
                    # Сбрасываем предыдущие фильтры
                    proxy.setFilterRegExp("")
                    
                    # Фильтрация по категории
                    if category_filter:
                        category_col = fields.index('Category')
                        proxy.setFilterKeyColumn(category_col)
                        proxy.setFilterFixedString(category_filter)
                    
                    # Фильтрация по поставщику
                    if supplier_filter:
                        supplier_col = fields.index('Supplier')
                        proxy.setFilterKeyColumn(supplier_col)
                        proxy.setFilterFixedString(supplier_filter)
                else:
                    # Сбрасываем фильтры
                    proxy.setFilterRegExp("")
            
            filter_button.clicked.connect(show_filter_dialog)


        if not is_admin and title == "Сотрудники":
            table.setColumnHidden(5, True)
            table.setColumnHidden(7, True)
        if not is_admin or is_employee:
            table.setEditTriggers(QTableView.NoEditTriggers)

        vbox.addWidget(table)
        
        # Поиск по кнопке — выделение подходящих строк
        def perform_search():
            search_text = search_input.text().lower()
            if search_text == "":
                self.refresh_current_tab()
                return
            
            table.clearSelection()

            if not search_text:
                return

            for row in range(model.rowCount()):
                match_found = False
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    if item and search_text in item.text().lower():
                        match_found = True
                if match_found:
                    table.selectRow(row)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        edit_btn = QPushButton("Редактировать")
        del_btn = QPushButton("Удалить")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        vbox.addLayout(btn_layout)

        if not is_admin and title == "Сотрудники":
            add_btn.setEnabled(False)
            del_btn.setEnabled(False)
            edit_btn.setEnabled(False)
        if not is_admin and title == "Заказы":
            del_btn.setEnabled(False)
        if title == "Заказы":
            edit_btn.setEnabled(False) 
        if title == "Поставки":
            edit_btn.setEnabled(False)
        if title == "Лекарства":
            edit_btn.setEnabled(False)

        search_button.clicked.connect(perform_search)

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
            dlg = MedicineAddRecordDialog(title="Лекарства", controllers=self.controllers)
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Заказы":
            dlg = OrderAddRecordDialog(title="Добавить сделку", controllers=self.controllers)
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Поставщики":
            dlg = SupplierAddRecordDialog(title="Добавить поставщика", controller=self.controllers['supplier'])
            if dlg.exec_() == QDialog.Accepted:
                self.refresh_current_tab()
        elif title == "Поставки":
            dlg = ShipmentAddRecordDialog(title="Добавить поставку", controllers=self.controllers)
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






def load_stylesheet(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("styles.qss"))
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
