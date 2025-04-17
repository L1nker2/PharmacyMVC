import customtkinter as ctk

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MedicineView(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller

        # Поле поиска
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Поиск")
        self.search_entry.pack(pady=10, padx=20, fill="x")

        # Заглушка таблицы
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(self.table_frame, text="Таблица медикаментов").pack(pady=20)

        # Форма ввода
        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20)
        fields = ["Название", "Количество", "Категория", "Поставщик", "Цена", "Описание", "Срок годности"]
        self.entries = {}
        for idx, field in enumerate(fields):
            row, col = divmod(idx, 4)
            ctk.CTkLabel(form, text=field).grid(row=row*2, column=col, padx=5, pady=(0, 2))
            entry = ctk.CTkEntry(form)
            entry.grid(row=row*2+1, column=col, padx=5, pady=(0, 5))
            self.entries[field] = entry

        ctk.CTkButton(self, text="Добавить", command=self.on_add).pack(pady=10)

    def on_add(self):
        # TODO: добавить медикамент
        data = {field: entry.get() for field, entry in self.entries.items()}
        if self.controller:
            self.controller.add_medication(data)