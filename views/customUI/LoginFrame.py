import customtkinter as ctk

class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback, registration_callback, *args, **kwargs):
        """
        Фрейм для аутентификации, объединяющий формы логина и регистрации.

        :param master: родительский виджет.
        :param login_callback: функция, вызываемая при попытке входа. Принимает login, password.
        :param registration_callback: функция для регистрации. Принимает login, password, role.
        """
        super().__init__(master, *args, **kwargs)
        self.login_callback = login_callback
        self.registration_callback = registration_callback
        self.create_widgets()

    def create_widgets(self):
        # Создаем Tabview для переключения между входом и регистрацией
        self.tabview = ctk.CTkTabview(self, width=400, height=400)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Добавляем вкладку "Вход" и создаем форму входа
        self.tabview.add("Вход")
        self.create_login_tab(self.tabview.tab("Вход"))

        # Добавляем вкладку "Регистрация" и создаем форму регистрации
        self.tabview.add("Регистрация")
        self.create_registration_tab(self.tabview.tab("Регистрация"))

    def create_login_tab(self, tab):
        # Заголовок формы входа
        self.login_title = ctk.CTkLabel(tab, text="Вход в систему", font=("Arial", 20, "bold"))
        self.login_title.pack(pady=(20, 10))

        # Поле ввода логина
        self.login_entry = ctk.CTkEntry(tab, placeholder_text="Логин", width=250)
        self.login_entry.pack(pady=10)

        # Поле ввода пароля
        self.password_entry = ctk.CTkEntry(tab, placeholder_text="Пароль", show="*", width=250)
        self.password_entry.pack(pady=10)

        # Кнопка "Войти"
        self.login_button = ctk.CTkButton(tab, text="Войти", command=self.on_login)
        self.login_button.pack(pady=(10, 10))

        # Выпадающий список для выбора роли
        self.reg_role_option = ctk.CTkOptionMenu(tab, values=["Сотрудник", "Пользователь"], width=250)
        self.reg_role_option.set("Пользователь")  # значение по умолчанию
        self.reg_role_option.pack(pady=10)

        # Метка для вывода сообщений (ошибок/успеха)
        self.login_message = ctk.CTkLabel(tab, text="", fg_color="transparent", text_color="red")
        self.login_message.pack(pady=(0, 10))

    def create_registration_tab(self, tab):
        # Заголовок формы регистрации
        self.reg_title = ctk.CTkLabel(tab, text="Регистрация", font=("Arial", 20, "bold"))
        self.reg_title.pack(pady=(20, 10))

        # Поле ввода имени
        self.reg_FName_entry = ctk.CTkEntry(tab, placeholder_text="Имя", width=250)
        self.reg_FName_entry.pack(pady=10)

        # Поле ввода фамилии
        self.reg_SName_entry = ctk.CTkEntry(tab, placeholder_text="Фамилия", width=250)
        self.reg_SName_entry.pack(pady=10)

        # Поле ввода телефона
        self.reg_number_entry = ctk.CTkEntry(tab, placeholder_text="Телефон", width=250)
        self.reg_number_entry.pack(pady=10)

        # Поле ввода логина
        self.reg_login_entry = ctk.CTkEntry(tab, placeholder_text="Логин", width=250)
        self.reg_login_entry.pack(pady=10)

        # Поле ввода пароля
        self.reg_password_entry = ctk.CTkEntry(tab, placeholder_text="Пароль", show="*", width=250)
        self.reg_password_entry.pack(pady=10)

        # Выпадающий список для выбора роли
        self.reg_role_option = ctk.CTkOptionMenu(tab, values=["Пользователь"], width=250)
        self.reg_role_option.set("Пользователь")  # значение по умолчанию
        self.reg_role_option.pack(pady=10)

        # Кнопка регистрации
        self.register_button = ctk.CTkButton(tab, text="Зарегистрироваться", command=self.on_register)
        self.register_button.pack(pady=(10, 10))

        # Метка для вывода сообщений (ошибок/успеха)
        self.reg_message = ctk.CTkLabel(tab, text="", fg_color="transparent", text_color="red")
        self.reg_message.pack(pady=(0, 10))

    def on_login(self):
        # Получаем данные для входа
        login = self.login_entry.get()
        password = self.password_entry.get()
        role = self.reg_role_option.get()

        if not login or not password:
            self.login_message.configure(text="Пожалуйста, заполните все поля")
            return

        success = self.login_callback(login, password, role)
        if success:
            self.login_message.configure(text="Успешный вход", text_color="green")
        else:
            self.login_message.configure(text="Ошибка входа", text_color="red")

    def on_register(self):
        # Получаем данные для регистрации
        fname = self.reg_FName_entry.get()
        sname = self.reg_SName_entry.get()
        number = self.reg_number_entry.get()
        login = self.reg_login_entry.get()
        password = self.reg_password_entry.get()
        registration_data = {
            'FName': fname,
            'LName': sname,
            'Number': number,
            'Login': login,
            'Pass': password,
            'Balance': 0.00
        }
        role = self.reg_role_option.get()

        if not fname or not sname or not number or not login or not password:
            self.reg_message.configure(text="Пожалуйста, заполните все поля")
            return

        success = self.registration_callback(registration_data, role)
        if success:
            self.reg_message.configure(text="Регистрация успешна", text_color="green")
        else:
            self.reg_message.configure(text="Ошибка регистрации", text_color="red")


