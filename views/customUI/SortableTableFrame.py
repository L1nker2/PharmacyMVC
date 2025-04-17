import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SortableTableFrame(ctk.CTkFrame):
    def __init__(self, master, headers, data, delete_event, edit_event, *args, **kwargs):
        """
        headers: список заголовков столбцов
        data: список строк, каждая строка – список значений для столбцов
        delete_event: callback при удалении (получает ID или объект строки)
        edit_event: callback при редактировании (получает объект строки)
        """
        super().__init__(master, *args, **kwargs)
        # Добавляем столбец для действий
        self.headers = headers + ["Действие"]
        self.data = data
        self.delete_event = delete_event
        self.edit_event = edit_event
        # Для каждого столбца (кроме колонки действий) храним порядок сортировки
        self.sort_orders = [True] * len(headers)
        self.create_table()

    def create_table(self):
        # Очищаем предыдущие виджеты
        for widget in self.winfo_children():
            widget.destroy()

        # Шапка таблицы
        for col, header in enumerate(self.headers):
            if header == "Действие":
                hdr = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            else:
                hdr = ctk.CTkButton(
                    self,
                    text=header,
                    font=("Arial", 14, "bold"),
                    command=lambda c=col: self.sort_by_column(c)
                )
            hdr.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

        # Строки таблицы
        for row_idx, row in enumerate(self.data, start=1):
            # Ячейки
            for col_idx, cell in enumerate(row):
                lbl = ctk.CTkLabel(self, text=str(cell), font=("Arial", 12))
                lbl.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="nsew")
            # Кнопки действий
            action_frame = ctk.CTkFrame(self)
            action_frame.grid(
                row=row_idx,
                column=len(self.headers) - 1,
                padx=10,
                pady=5,
                sticky="nsew"
            )
            edit_btn = ctk.CTkButton(
                action_frame,
                text="Edit",
                width=60,
                command=lambda r=row: self.edit_event(r)
            )
            edit_btn.pack(side="left", padx=5)
            delete_btn = ctk.CTkButton(
                action_frame,
                text="Del",
                width=60,
                command=lambda r=row: self.delete_event(r)
            )
            delete_btn.pack(side="left", padx=5)

        # Конфигурируем веса колонок и строк
        for col in range(len(self.headers)):
            self.grid_columnconfigure(col, weight=1)
        for r in range(len(self.data) + 1):
            self.grid_rowconfigure(r, minsize=40)

    def sort_by_column(self, col_index):
        # Переключаем порядок сортировки
        self.sort_orders[col_index] = not self.sort_orders[col_index]
        ascending = self.sort_orders[col_index]
        # Сортируем данные
        self.data.sort(key=lambda row: row[col_index], reverse=not ascending)
        self.create_table()

    def update_data(self, new_data):
        """
        Обновляет строки таблицы новым списком.
        """
        self.data = new_data
        self.create_table()
