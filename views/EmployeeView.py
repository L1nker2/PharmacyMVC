import customtkinter as ctk
from views.customUI.SortableTableFrame import SortableTableFrame

# Устанавливаем тёмную тему по умолчанию
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EmployeesView(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller
        self.all_employees = self.controller.get_all()
        self.headers = ["Айди", "Имя", "Фамилия", "Телефон", "Логин", "Дата рождения", "Должность", "Администратор"]

        # Поисковая строка
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Поиск", textvariable=self.search_var)
        self.search_entry.pack(pady=10, padx=20, fill="x")
        self.search_var.trace_add("write", self.on_search)

        # Таблица
        self.table_frame = SortableTableFrame(master=self, headers=self.headers, data=self.all_employees,
                                              edit_event=self.edit_event(), delete_event=self.delete_event())
        self.table_frame.pack(padx=20, pady=5, fill="x")

        # Форма ввода
        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20)
        fields = ["Фамилия", "Телефон", "Логин", "Дата рождения", "Имя", "Должность", "Пароль", "Администратор"]
        self.entries = {}
        for idx, field in enumerate(fields):
            row, col = divmod(idx, 4)
            ctk.CTkLabel(form, text=field).grid(row=row * 2, column=col, padx=5, pady=(0, 2))
            entry = ctk.CTkEntry(form)
            entry.grid(row=row * 2 + 1, column=col, padx=5, pady=(0, 5))
            self.entries[field] = entry
        ctk.CTkButton(self, text="Добавить", command=self.on_add).pack(pady=10)

        ctk.CTkButton(self, text="Добавить", command=self.on_add).pack(pady=10)

    def on_add(self):
        data = {field: entry.get() for field, entry in self.entries.items()}
        if self.controller and hasattr(self.controller, 'add_employee'):
            self.controller.add_employee(data)

    def edit_event(self):
        pass
    def delete_event(self):
        pass

    def on_search(self, *args):
        query = self.search_var.get().lower()
        filtered = [row for row in self.all_employees if any(query in str(val).lower() for val in row)]
        self.table_frame.update_data(filtered)