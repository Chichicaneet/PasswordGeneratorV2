from PySide6.QtWidgets import (    
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QComboBox, QGroupBox
)
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet, list_themes
from saved_data_window import SavedDataWindow
from database import Database
from password_generator import generate_password
import os

class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_theme = True  # По умолчанию включена темная тема
        self.language = "ru"  # По умолчанию язык — русский
        self.translations = self.load_translations()  # Загружаем переводы
        self.db = Database()  # Инициализируем базу данных

        # Устанавливаем иконку для окна
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'app_icon.ico'))
        

        self.init_ui()

        # Применяем Material Design тему по умолчанию
        apply_stylesheet(self, theme='dark_purple.xml')  # Применяем темную тему с акцентом на teal

    def load_translations(self):
        """Загружает переводы для интерфейса."""
        return {
            "ru": {
                "site_label": "Название сайта/приложения (необязательно):",
                "login_label": "Логин (необязательно):",
                "length_label": "Длина пароля:",
                "generate_button": "Сгенерировать пароль",
                "numbers_check": "Использовать цифры",
                "letters_check": "Использовать буквы",
                "symbols_check": "Использовать символы",
                "numbers_count_label": "Количество цифр:",
                "letters_count_label": "Количество букв:",
                "symbols_count_label": "Количество символов:",
                "password_label": "Сгенерированный пароль:",
                "save_button": "Сохранить данные",
                "theme_label": "Выберите тему:",
                "open_file_button": "Открыть сохраненные данные",
                "change_language": "Сменить язык на английский",
                "error_length": "Введите корректную длину пароля (целое число больше 0).",
                "error_symbols": "Выберите хотя бы один тип символов.",
                "error_password": "Сначала сгенерируйте пароль.",
                "error_duplicate": "Пароль для этого сайта уже существует.",
                "success_save": "Данные успешно сохранены.",
                "back_button": "Назад"
            },
            "en": {
                "site_label": "Website/application name (optional):",
                "login_label": "Login (optional):",
                "length_label": "Password length:",
                "generate_button": "Generate password",
                "numbers_check": "Use digits",
                "letters_check": "Use letters",
                "symbols_check": "Use symbols",
                "numbers_count_label": "Number of digits:",
                "letters_count_label": "Number of letters:",
                "symbols_count_label": "Number of symbols:",
                "password_label": "Generated password:",
                "save_button": "Save data",
                "theme_label": "Select theme:",
                "open_file_button": "Open saved data",
                "change_language": "Switch to Russian",
                "error_length": "Please enter a valid password length (integer greater than 0).",
                "error_symbols": "Please select at least one type of symbols.",
                "error_password": "Please generate a password first.",
                "error_duplicate": "A password for this website already exists.",
                "success_save": "Data successfully saved.",
                "back_button": "Back"
            }
        }

    def init_ui(self):
        self.setWindowTitle("Генератор паролей" if self.language == "ru" else "Password Generator")
        self.setGeometry(100, 100, 600, 450)  # Увеличиваем ширину окна

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # Уменьшаем отступы между элементами

        # Горизонтальный layout для верхней части (ввод данных и выбор символов)
        top_layout = QHBoxLayout()

        # Блок для ввода данных (сайт, логин, длина пароля)
        self.input_group = QGroupBox("Данные для генерации" if self.language == "ru" else "Generation Data")
        input_layout = QVBoxLayout()

        # Поле для ввода названия сайта/приложения
        self.site_label = QLabel(self.translations[self.language]["site_label"])
        self.site_input = QLineEdit()
        input_layout.addWidget(self.site_label)
        input_layout.addWidget(self.site_input)

        # Поле для ввода логина
        self.login_label = QLabel(self.translations[self.language]["login_label"])
        self.login_input = QLineEdit()
        input_layout.addWidget(self.login_label)
        input_layout.addWidget(self.login_input)

        # Поле для ввода длины пароля
        self.length_label = QLabel(self.translations[self.language]["length_label"])
        self.length_input = QLineEdit()
        self.length_input.setFixedWidth(50)
        input_layout.addWidget(self.length_label)
        input_layout.addWidget(self.length_input)

        self.input_group.setLayout(input_layout)
        top_layout.addWidget(self.input_group)

        # Блок для выбора символов
        self.symbols_group = QGroupBox("Типы символов" if self.language == "ru" else "Symbol Types")
        symbols_layout = QVBoxLayout()

        # Чекбоксы для выбора типов символов
        self.numbers_check = QCheckBox(self.translations[self.language]["numbers_check"])
        self.numbers_check.setChecked(True)
        symbols_layout.addWidget(self.numbers_check)

        # Поле для ввода количества цифр
        self.numbers_count_label = QLabel(self.translations[self.language]["numbers_count_label"])
        self.numbers_count_input = QLineEdit()
        self.numbers_count_input.setFixedWidth(50)
        symbols_layout.addWidget(self.numbers_count_label)
        symbols_layout.addWidget(self.numbers_count_input)

        self.letters_check = QCheckBox(self.translations[self.language]["letters_check"])
        self.letters_check.setChecked(True)
        symbols_layout.addWidget(self.letters_check)

        # Поле для ввода количества букв
        self.letters_count_label = QLabel(self.translations[self.language]["letters_count_label"])
        self.letters_count_input = QLineEdit()
        self.letters_count_input.setFixedWidth(50)
        symbols_layout.addWidget(self.letters_count_label)
        symbols_layout.addWidget(self.letters_count_input)

        self.symbols_check = QCheckBox(self.translations[self.language]["symbols_check"])
        self.symbols_check.setChecked(True)
        symbols_layout.addWidget(self.symbols_check)

        # Поле для ввода количества символов
        self.symbols_count_label = QLabel(self.translations[self.language]["symbols_count_label"])
        self.symbols_count_input = QLineEdit()
        self.symbols_count_input.setFixedWidth(50)
        symbols_layout.addWidget(self.symbols_count_label)
        symbols_layout.addWidget(self.symbols_count_input)

        self.symbols_group.setLayout(symbols_layout)
        top_layout.addWidget(self.symbols_group)

        main_layout.addLayout(top_layout)

        # Блок для отображения сгенерированного пароля
        self.password_group = QGroupBox("Сгенерированный пароль" if self.language == "ru" else "Generated Password")
        password_layout = QVBoxLayout()

        self.password_label = QLabel(self.translations[self.language]["password_label"])
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_output)

        self.password_group.setLayout(password_layout)
        main_layout.addWidget(self.password_group)

        # Горизонтальный layout для кнопок управления и настроек
        bottom_layout = QHBoxLayout()

        # Блок для кнопок управления
        self.buttons_group = QGroupBox("Управление" if self.language == "ru" else "Controls")
        buttons_layout = QVBoxLayout()

        # Кнопка генерации пароля
        self.generate_button = QPushButton(self.translations[self.language]["generate_button"])
        self.generate_button.clicked.connect(self.generate_password)
        buttons_layout.addWidget(self.generate_button)

        # Кнопка сохранения данных
        self.save_button = QPushButton(self.translations[self.language]["save_button"])
        self.save_button.clicked.connect(self.save_data)
        buttons_layout.addWidget(self.save_button)

        self.buttons_group.setLayout(buttons_layout)
        bottom_layout.addWidget(self.buttons_group)

        # Блок для настроек (тема, язык, открытие данных)
        self.settings_group = QGroupBox("Настройки" if self.language == "ru" else "Settings")
        settings_layout = QVBoxLayout()

        # Выбор темы
        self.theme_label = QLabel(self.translations[self.language]["theme_label"])
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(list_themes())
        self.theme_combobox.setCurrentText('dark_purple.xml')  # Устанавливаем тему по умолчанию
        self.theme_combobox.currentTextChanged.connect(self.change_theme)
        settings_layout.addWidget(self.theme_label)
        settings_layout.addWidget(self.theme_combobox)

        # Кнопка для открытия сохраненных данных
        self.open_file_button = QPushButton(self.translations[self.language]["open_file_button"])
        self.open_file_button.clicked.connect(self.show_saved_data)
        settings_layout.addWidget(self.open_file_button)

        # Кнопка для смены языка
        self.change_language_button = QPushButton(self.translations[self.language]["change_language"])
        self.change_language_button.clicked.connect(self.change_language)
        settings_layout.addWidget(self.change_language_button)

        self.settings_group.setLayout(settings_layout)
        bottom_layout.addWidget(self.settings_group)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def change_theme(self, theme_name):
        """Применяет выбранную тему."""
        apply_stylesheet(self, theme=theme_name)

    def change_language(self):
        """Переключает язык интерфейса."""
        self.language = "en" if self.language == "ru" else "ru"
        self.update_ui_text()

    def update_ui_text(self):
        """Обновляет текст всех элементов интерфейса в соответствии с текущим языком."""
        self.setWindowTitle("Генератор паролей" if self.language == "ru" else "Password Generator")
        self.site_label.setText(self.translations[self.language]["site_label"])
        self.login_label.setText(self.translations[self.language]["login_label"])
        self.length_label.setText(self.translations[self.language]["length_label"])
        self.generate_button.setText(self.translations[self.language]["generate_button"])
        self.numbers_check.setText(self.translations[self.language]["numbers_check"])
        self.letters_check.setText(self.translations[self.language]["letters_check"])
        self.symbols_check.setText(self.translations[self.language]["symbols_check"])
        self.numbers_count_label.setText(self.translations[self.language]["numbers_count_label"])
        self.letters_count_label.setText(self.translations[self.language]["letters_count_label"])
        self.symbols_count_label.setText(self.translations[self.language]["symbols_count_label"])
        self.password_label.setText(self.translations[self.language]["password_label"])
        self.save_button.setText(self.translations[self.language]["save_button"])
        self.theme_label.setText(self.translations[self.language]["theme_label"])
        self.open_file_button.setText(self.translations[self.language]["open_file_button"])
        self.change_language_button.setText(self.translations[self.language]["change_language"])
        
        # Обновляем заголовки QGroupBox
        self.input_group.setTitle("Данные для генерации" if self.language == "ru" else "Generation Data")
        self.symbols_group.setTitle("Типы символов" if self.language == "ru" else "Symbol Types")
        self.password_group.setTitle("Сгенерированный пароль" if self.language == "ru" else "Generated Password")
        self.buttons_group.setTitle("Управление" if self.language == "ru" else "Controls")
        self.settings_group.setTitle("Настройки" if self.language == "ru" else "Settings")

    def generate_password(self):
        """Генерирует пароль с использованием функции из password_generator.py."""
        password = generate_password(
            self.length_input,
            self.numbers_check,
            self.letters_check,
            self.symbols_check,
            self.numbers_count_input,
            self.letters_count_input,
            self.symbols_count_input,
            self.language,
            self
        )
        if password:
            self.password_output.setText(password)

    def save_data(self):
        site = self.site_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_output.text().strip()

        if not password:
            QMessageBox.warning(self, "Ошибка", self.translations[self.language]["error_password"])
            return

        # Проверка на дубликаты
        if self.db.password_exists(site):
            QMessageBox.warning(self, "Ошибка", self.translations[self.language]["error_duplicate"])
            return

        # Сохранение пароля в исходном виде
        self.db.save_password(site, login, password)

        QMessageBox.information(self, "Успех", self.translations[self.language]["success_save"])

    def show_saved_data(self):
        """Открывает новое окно с сохраненными данными."""
        current_theme = self.theme_combobox.currentText()
        self.saved_data_window = SavedDataWindow(self.db, self.language, self, current_theme)
        self.saved_data_window.show()
        
        