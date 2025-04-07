import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SortableTableFrame(ctk.CTkFrame):
    def __init__(self, master, headers, data, delete_event, edit_event, *args, **kwargs):
        """
        headers: список заголовков столбцов (например, ["ID", "Name", "Price", "Category"])
        data: список строк, каждая строка – список значений для столбцов (например, [[1, "Aspirin", 5.00, "Painkiller"], ...])
        """
        super().__init__(master, *args, **kwargs)
        # Дополнительно добавляем столбец для действий
        self.headers = headers + ["Действие"]
        self.data = data
        self.edit_event = edit_event
        self.delete_event = delete_event
        # Для каждого столбца (исключая столбец действий) храним состояние сортировки (True - по возрастанию)
        self.sort_orders = [True] * len(headers)
        self.create_table()

    def create_table(self):
        # Очистка предыдущих виджетов, если таблица перерисовывается
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем заголовки: для каждого столбца (кроме "Действие") используем кнопку, по нажатию на которую происходит сортировка
        for col, header in enumerate(self.headers):
            if header == "Действие":
                header_widget = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            else:
                # Используем lambda с аргументом col, чтобы не было проблемы с замыканием
                header_widget = ctk.CTkButton(self, text=header, font=("Arial", 14, "bold"),
                                              command=lambda c=col: self.sort_by_column(c))
            header_widget.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

        # Создаем строки с данными
        for row_index, row in enumerate(self.data, start=1):
            # Для каждого значения в строке создаем label
            for col_index, cell in enumerate(row):
                cell_label = ctk.CTkLabel(self, text=str(cell), font=("Arial", 12))
                cell_label.grid(row=row_index, column=col_index, padx=10, pady=5, sticky="nsew")
            # В последнем столбце создаем фрейм с кнопками для редактирования и удаления
            action_frame = ctk.CTkFrame(self)
            action_frame.grid(row=row_index, column=len(self.headers)-1, padx=10, pady=5, sticky="nsew")
            edit_button = ctk.CTkButton(action_frame, text="Edit", width=60,
                                        command=lambda r=row: self.edit_event(r))
            edit_button.pack(side="left", padx=5)
            delete_button = ctk.CTkButton(action_frame, text="Del", width=60,
                                          command=lambda r=row: self.delete_event(r.id))
            delete_button.pack(side="left", padx=5)

        # Настраиваем веса колонок и строк для равномерного распределения
        for col in range(len(self.headers)):
            self.grid_columnconfigure(col, weight=1)
        for row in range(len(self.data) + 1):
            self.grid_rowconfigure(row, minsize=40)

    def sort_by_column(self, col_index):
        # Переключаем порядок сортировки для выбранного столбца
        self.sort_orders[col_index] = not self.sort_orders[col_index]
        ascending = self.sort_orders[col_index]
        # Сортируем данные по выбранной колонке
        self.data.sort(key=lambda row: row[col_index], reverse=not ascending)
        self.create_table()  # Перерисовываем таблицу
