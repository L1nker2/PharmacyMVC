import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SortableTableFrame(ctk.CTkFrame):
    def __init__(self, master, headers, data, *args, **kwargs):
        """
        headers: список заголовков столбцов (например, ["ID", "Name", "Price", "Category"])
        data: список строк, каждая строка – список значений для столбцов (например, [[1, "Aspirin", 5.00, "Painkiller"], ...])
        """
        super().__init__(master, *args, **kwargs)
        # Дополнительно добавляем столбец для действий
        self.headers = headers + ["Actions"]
        self.data = data
        # Для каждого столбца (исключая столбец действий) храним состояние сортировки (True - по возрастанию)
        self.sort_orders = [True] * len(headers)
        self.create_table()

    def create_table(self):
        # Очистка предыдущих виджетов, если таблица перерисовывается
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем заголовки: для каждого столбца (кроме "Actions") используем кнопку, по нажатию на которую происходит сортировка
        for col, header in enumerate(self.headers):
            if header == "Actions":
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
                                        command=lambda r=row: self.edit_record(r))
            edit_button.pack(side="left", padx=5)
            delete_button = ctk.CTkButton(action_frame, text="Delete", width=60,
                                          command=lambda r=row: self.delete_record(r))
            delete_button.pack(side="left", padx=5)

        # Настраиваем веса колонок и строк для равномерного распределения
        for col in range(len(self.headers)):
            self.grid_columnconfigure(col, weight=1)
        for row in range(len(self.data) + 1):
            self.grid_rowconfigure(row, weight=1)

    def sort_by_column(self, col_index):
        # Переключаем порядок сортировки для выбранного столбца
        self.sort_orders[col_index] = not self.sort_orders[col_index]
        ascending = self.sort_orders[col_index]
        # Сортируем данные по выбранной колонке
        self.data.sort(key=lambda row: row[col_index], reverse=not ascending)
        self.create_table()  # Перерисовываем таблицу

    def edit_record(self, row):
        # Здесь можно реализовать открытие окна редактирования для выбранной записи
        print("Edit record:", row)

    def delete_record(self, row):
        # Реализуем удаление записи и обновление таблицы
        print("Delete record:", row)
        self.data.remove(row)
        self.create_table()

def main():
    root = ctk.CTk()
    root.geometry("800x600")
    root.title("Sortable Table with Actions")

    headers = ["ID", "Name", "Price", "Category"]
    data = [
        [1, "Aspirin", 5.00, "Painkiller"],
        [2, "Paracetamol", 4.50, "Antipyretic"],
        [3, "Ibuprofen", 6.00, "Anti-inflammatory"],
        [4, "Vitamin C", 3.50, "Supplement"]
    ]

    table = SortableTableFrame(root, headers, data)
    table.pack(padx=20, pady=20, fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
