from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMenu, QMessageBox, QApplication, QHBoxLayout, QCheckBox, QInputDialog
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

        # Основной layout
        layout = QVBoxLayout()

        # Чекбокс "Выделить все"
        self.select_all_checkbox = QCheckBox("Выделить все" if self.language == "ru" else "Select All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(self.select_all_checkbox)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Сайт/Приложение", "Логин", "Пароль"] if self.language == "ru" else ["Website/Application", "Login", "Password"]
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
        self.table.setColumnWidth(0, 300)  # Ширина столбца "Сайт/Приложение"
        self.table.setColumnWidth(1, 200)  # Ширина столбца "Логин"
        self.table.setColumnWidth(2, 200)  # Ширина столбца "Пароль"

        for row, (id, site, login, password) in enumerate(data):
            # Добавляем данные в таблицу
            self.table.setItem(row, 0, QTableWidgetItem(site))
            self.table.setItem(row, 1, QTableWidgetItem(login))

            # Поле для пароля с режимом Password (звездочки)
            password_item = QTableWidgetItem(password)
            password_item.setData(Qt.ItemDataRole.UserRole, id)  # Сохраняем ID
            password_item.setFlags(password_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Запрещаем редактирование
            self.table.setItem(row, 2, password_item)

            # Устанавливаем режим отображения пароля (звездочки)
            self.table.item(row, 2).setText("*" * 8)  # Показываем звездочки

            # Делаем текст в ячейках выравненным по левому краю
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row, 2).setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Подключаем обработчик двойного клика для отображения пароля
        self.table.cellDoubleClicked.connect(self.show_password)

    def show_password(self, row, column):
        """Показывает реальный пароль при двойном клике на ячейку."""
        if column == 2:  # Если кликнули на ячейку с паролем
            item = self.table.item(row, column)
            real_password = item.data(Qt.ItemDataRole.UserRole + 1)  # Получаем реальный пароль
            if real_password:
                item.setText(real_password)  # Показываем реальный пароль
            else:
                # Если реальный пароль не сохранен, получаем его из базы данных
                id = item.data(Qt.ItemDataRole.UserRole)
                self.cursor.execute("SELECT password FROM passwords WHERE id = ?", (id,))
                real_password = self.cursor.fetchone()[0]
                item.setData(Qt.ItemDataRole.UserRole + 1, real_password)  # Сохраняем пароль
                item.setText(real_password)  # Показываем реальный пароль

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
            id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # Получаем ID из скрытых данных
            site = self.table.item(row, 0).text()
            login = self.table.item(row, 1).text()
            password = self.table.item(row, 2).text()

            # Обновляем запись в базе данных
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
            password = self.table.item(row, 2).text()
            data.append((id, site, login, password))
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
            self.db.restore_backup()  # Восстановление ба