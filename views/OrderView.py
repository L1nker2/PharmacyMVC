import customtkinter as ctk

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OrderView(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller

        # Поле поиска
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Поиск")
        self.search_entry.pack(pady=10, padx=20, fill="x")

        # Заглушка таблицы
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(self.table_frame, text="Таблица продаж").pack(pady=20)

        # Форма ввода
        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20, fill="x")
        # Дата
        self.date_entry = ctk.CTkEntry(form, placeholder_text="Дата")
        self.date_entry.grid(row=0, column=0, padx=5, pady=5)
        # Медикамент
        self.medic_combobox = ctk.CTkComboBox(form, values=[])
        self.medic_combobox.grid(row=0, column=1, padx=5, pady=5)
        # Количество
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Количество")
        self.qty_entry.grid(row=0, column=2, padx=5, pady=5)
        # Статус
        self.status_combobox = ctk.CTkComboBox(form, values=["Создано", "Отправлено", "Доставлено"])
        self.status_combobox.grid(row=0, column=3, padx=5, pady=5)
        # Кнопка добавить
        ctk.CTkButton(form, text="Добавить", command=self.on_add).grid(row=0, column=4, padx=10, pady=5)

    def on_add(self):
        # TODO: добавить запись о продаже
        data = {
            'date': self.date_entry.get(),
            'medicament': self.medic_combobox.get(),
            'quantity': self.qty_entry.get(),
            'status': self.status_combobox.get()
        }
        if self.controller:
            self.controller.add_sale(data)