from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMenu, 
    QMessageBox, QApplication, QHBoxLayout, QCheckBox, QInputDialog, QLabel, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from qt_material import apply_stylesheet  # Импортируем apply_stylesheet

class SavedDataWindow(QDialog):
    def __init__(self, db, language="ru", parent=None, theme_name=None):
        super().__init__(parent)
        self.db = db
        self.language = language
        self.theme_name = theme_name
        self.setWindowTitle("Сохраненные данные" if self.language == "ru" else "Saved Data")
        self.setGeometry(150, 150, 800, 450)  # Увеличим размер окна
        self.db.create_backup()  # Создание временной копии данных при открытии

        # Переменная для хранения текущего открытого пароля
        self.current_open_password = None   # Переменная для хранения текущего открытого пароля

        # Флаг для отслеживания двойного нажатия
        self.is_double_click = False
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Поле для поиска
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Поиск:" if self.language == "ru" else "Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название сайта/приложения..." if self.language == "ru" else "Enter website/application name...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        layout.addLayout(self.search_layout)


        # Чекбокс "Выделить все"
        self.select_all_checkbox = QCheckBox("Выделить все" if self.language == "ru" else "Select All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(self.select_all_checkbox)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Сайт/Приложение", "Логин", "Пароль", "Дата"] if self.language == "ru" else ["Website/Application", "Login", "Password", "Date"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)  # Разрешаем редактирование по двойному клику
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выделение строк
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)  # Разрешаем выделение нескольких строк
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Растягиваем столбцы
        self.table.verticalHeader().setVisible(False)  # Скрываем вертикальные заголовки

        # Включаем контекстное меню для копирования
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Горизонтальный layout для кнопок
        button_layout = QHBoxLayout()

        # Кнопка "Сохранить изменения"
        self.save_button = QPushButton("Сохранить изменения" if self.language == "ru" else "Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        # Кнопка "Отменить изменения"
        self.undo_button = QPushButton("Отменить изменения" if self.language == "ru" else "Undo Changes")
        self.undo_button.clicked.connect(self.undo_changes)
        button_layout.addWidget(self.undo_button)

        # Кнопка "Добавить запись"
        self.add_button = QPushButton("Добавить запись" if self.language == "ru" else "Add Entry")
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)

        # Кнопка "Удалить запись"
        self.delete_button = QPushButton("Удалить запись" if self.language == "ru" else "Delete Entry")
        self.delete_button.clicked.connect(self.delete_entry)
        button_layout.addWidget(self.delete_button)

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад" if self.language == "ru" else "Back")
        self.back_button.clicked.connect(self.close)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загружаем данные из базы данных
        self.load_data()

        # Применяем стили qt_material
        self.apply_theme()

        # Переменная для хранения последнего состояния данных
        self.last_state = self.get_current_table_data()

    def apply_theme(self):
        """Применяет тему из qt_material."""
        if self.theme_name:  # Если тема передана, используем её
            apply_stylesheet(self, theme=self.theme_name)
        else:  # Иначе используем тему по умолчанию
            apply_stylesheet(self, theme='dark_teal.xml')
            
    def load_data(self):
        """Загружает данные из базы данных и отображает их в таблице."""
        data = self.db.get_all_passwords()
        self.table.setRowCount(len(data))

        # Устанавливаем ширину столбцов
        self.table.setColumnWidth(0, 250)  # Ширина столбца "Сайт/Приложение"
        self.table.setColumnWidth(1, 150)  # Ширина столбца "Логин"
        self.table.setColumnWidth(2, 150)  # Ширина столбца "Пароль"
        self.table.setColumnWidth(3, 150)  # Ширина столбца "Дата добавления"

        for row, (id, site, login, password, created_at) in enumerate(data):
            # Добавляем данные в таблицу
            self.table.setItem(row, 0, QTableWidgetItem(site))
            self.table.setItem(row, 1, QTableWidgetItem(login))

            # Создаем QLineEdit для пароля
            password_edit = QLineEdit(password)
            password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Скрываем пароль
            password_edit.setReadOnly(True)  # Запрещаем редактирование
            password_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Разрешаем фокус

            # Показываем пароль при получении фокуса
            password_edit.installEventFilter(self)  # Устанавливаем фильтр событий

            self.table.setCellWidget(row, 2, password_edit)

            self.table.setItem(row, 3, QTableWidgetItem(created_at))

            # Сохраняем ID в скрытом виде
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, id)

            # Выравниваем текст по левому краю
            for col in range(4):
                if col != 2:  # Пропускаем столбец с паролем
                    self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def eventFilter(self, obj, event):
        """Обрабатывает события фокуса для QLineEdit."""
        if isinstance(obj, QLineEdit):
            if event.type() == event.Type.FocusIn:
                obj.setEchoMode(QLineEdit.EchoMode.Normal)  # Показываем пароль
            elif event.type() == event.Type.FocusOut:
                obj.setEchoMode(QLineEdit.EchoMode.Password)  # Скрываем пароль
                obj.deselect()  # Сбрасываем выделение текста
        return super().eventFilter(obj, event)  # Передаем событие дальше
                    
    def show_password(self, widget):
        """Показывает пароль при нажатии на поле."""
        widget.setEchoMode(QLineEdit.EchoMode.Normal)  # Показываем пароль
        widget.setFocus()  # Устанавливаем фокус на поле
        
    def hide_password(self, widget, event):
        """Скрывает пароль, когда поле теряет фокус."""
        widget.setEchoMode(QLineEdit.EchoMode.Password)  # Скрываем пароль
        widget.deselect()  # Сбрасываем выделение текста
        event.ignore()  # Позволяем событию focusOutEvent продолжить обработку
    
    def toggle_password_visibility(self, widget):
        """Переключает видимость пароля."""
        if self.current_open_password and self.current_open_password != widget:
            # Скрываем предыдущий открытый пароль
            self.current_open_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        if widget.echoMode() == QLineEdit.EchoMode.Password:
            widget.setEchoMode(QLineEdit.EchoMode.Normal)  # Показываем пароль
            self.current_open_password = widget  # Запоминаем текущий открытый пароль
        else:
            widget.setEchoMode(QLineEdit.EchoMode.Password)  # Скрываем пароль
            self.current_open_password = None  # Сбрасываем текущий открытый пароль
            
    def mousePressEvent(self, event):
        """Обрабатывает клик по окну."""
        if self.current_open_password and not self.is_double_click:
            # Скрываем пароль, если клик был вне поля с паролем и это не двойное нажатие
            self.current_open_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.current_open_password = None  # Сбрасываем текущий открытый пароль

        self.is_double_click = False  # Сбрасываем флаг
        super().mousePressEvent(event)  # Вызываем родительский метод
        
    def mouseDoubleClickEvent(self, event):
        """Обрабатывает двойное нажатие мыши."""
        self.is_double_click = True  # Устанавливаем флаг
        super().mouseDoubleClickEvent(event)  # Вызываем родительский метод
    
    def filter_table(self):
        """Фильтрует таблицу по введенному тексту."""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            site = self.table.item(row, 0).text().lower()
            if search_text in site:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def show_context_menu(self, position):
        """Показывает контекстное меню для копирования данных."""
        menu = QMenu(self)
        copy_action = QAction("Копировать" if self.language == "ru" else "Copy", self)
        copy_action.triggered.connect(self.copy_selected_data)
        menu.addAction(copy_action)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def copy_selected_data(self):
        """Копирует выделенные данные в буфер обмена."""
        selected_items = self.table.selectedItems()
        if selected_items:
            text = "\t".join(item.text() for item in selected_items)  # Копируем данные через табуляцию
            QApplication.clipboard().setText(text)

    def save_changes(self):
        """Сохраняет изменения в базе данных."""
        for row in range(self.table.rowCount()):
            id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            site = self.table.item(row, 0).text()
            login = self.table.item(row, 1).text()

            # Получаем пароль из QLineEdit
            password_edit = self.table.cellWidget(row, 2)
            password = password_edit.text()

            self.db.update_password(id, site, login, password)

        # Обновляем последнее состояние данных
        self.last_state = self.get_current_table_data()

        QMessageBox.information(self, "Успех", "Изменения сохранены." if self.language == "ru" else "Changes saved.")

    def delete_entry(self):
        """Удаляет выделенные записи из базы данных."""
        selected_rows = set()  # Используем set для хранения уникальных индексов строк
        for item in self.table.selectedItems():
            selected_rows.add(item.row())  # Добавляем индекс строки в set

        if not selected_rows:
            QMessageBox.warning(
                self,
                "Ошибка" if self.language == "ru" else "Error",
                "Выберите записи для удаления." if self.language == "ru" else "Select entries to delete."
            )
            return

        # Отображаем диалоговое окно с подтверждением
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления" if self.language == "ru" else "Confirm Deletion",
            "Вы уверены, что хотите удалить выбранные записи?" if self.language == "ru" else "Are you sure you want to delete the selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Если пользователь подтвердил удаление
        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем записи из базы данных
            for row in sorted(selected_rows, reverse=True):  # Удаляем с конца, чтобы избежать смещения индексов
                id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # Получаем ID из скрытых данных
                self.db.delete_password(id)
                self.table.removeRow(row)  # Удаляем строку из таблицы

            # Обновляем последнее состояние данных
            self.last_state = self.get_current_table_data()

            QMessageBox.information(
                self,
                "Успех" if self.language == "ru" else "Success",
                "Записи удалены." if self.language == "ru" else "Entries deleted."
            )

    def toggle_select_all(self):
        """Выделяет или снимает выделение со всех строк."""
        if self.select_all_checkbox.isChecked():
            self.table.selectAll()  # Выделить все строки
        else:
            self.table.clearSelection()  # Снять выделение со всех строк

    def add_entry(self):
        """Добавляет новую запись в таблицу и базу данных."""
        # Диалоговое окно для ввода данных
        site, ok1 = QInputDialog.getText(self, "Добавить запись" if self.language == "ru" else "Add Entry", "Введите название сайта/приложения:" if self.language == "ru" else "Enter website/application name:")
        login, ok2 = QInputDialog.getText(self, "Добавить запись" if self.language == "ru" else "Add Entry", "Введите логин:" if self.language == "ru" else "Enter login:")
        password, ok3 = QInputDialog.getText(self, "Добавить запись" if self.language == "ru" else "Add Entry", "Введите пароль:" if self.language == "ru" else "Enter password:")

        if ok1 and ok2 and ok3:
            # Добавляем запись в базу данных
            self.db.save_password(site, login, password)

            # Обновляем таблицу
            self.load_data()

            # Обновляем последнее состояние данных
            self.last_state = self.get_current_table_data()

            QMessageBox.information(
                self,
                "Успех" if self.language == "ru" else "Success",
                "Запись добавлена." if self.language == "ru" else "Entry added."
            )

    def get_current_table_data(self):
        """Возвращает текущие данные из таблицы в виде списка кортежей."""
        data = []
        for row in range(self.table.rowCount()):
            id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            site = self.table.item(row, 0).text()
            login = self.table.item(row, 1).text()

            # Получаем пароль из QLineEdit
            password_edit = self.table.cellWidget(row, 2)
            password = password_edit.text()

            created_at = self.table.item(row, 3).text()
            data.append((id, site, login, password, created_at))
        return data

    def undo_changes(self):
        """Восстанавливает данные из временного файла при отмене изменений."""
        reply = QMessageBox.question(
            self,
            "Подтверждение отмены изменений" if self.language == "ru" else "Confirm Undo Changes",
            "Вы уверены, что хотите отменить изменения и восстановить удаленные записи?" if self.language == "ru" else "Are you sure you want to undo changes and restore deleted entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.restore_backup()  # Восстановление базы данных
            self.load_data()  # Перезагрузка данных в таблицу
            QMessageBox.information(
            self,
            "Успех" if self.language == "ru" else "Success",
            "Изменения отменены. Удаленные записи восстановлены." if self.language == "ru" else "Changes undone. Deleted entries restored."
        )
    
    def closeEvent(self, event):
        """Удаляет временную копию базы данных при закрытии окна."""
        self.db.delete_backup()
        event.accept()

