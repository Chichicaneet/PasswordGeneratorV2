from pathlib import Path
import sqlite3
import json

class Database:
    def __init__(self, db_name="passwords.db"):
        current_dir = Path(__file__).parent  # Получаем текущую директорию
        self.data_dir = current_dir / "data"  # Путь к папке data
        self.data_dir.mkdir(exist_ok=True)  # Создаем папку, если она не существует

        self.db_path = self.data_dir / db_name  # Путь к базе данных
        self.backup_path = self.data_dir / "backup.json"  # Путь к резервной копии JSON

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
                site TEXT,
                login TEXT,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- Добавляем столбец для даты
            )
        """)
        self.conn.commit()

    def save_password(self, site, login, password):
        """Сохраняет пароль в базе данных без хэширования."""
        self.cursor.execute("INSERT INTO passwords (site, login, password) VALUES (?, ?, ?)", 
                        (site, login, password))
        self.conn.commit()

    def get_all_passwords(self):
        """Возвращает все сохраненные пароли."""
        self.cursor.execute("SELECT id, site, login, password, created_at FROM passwords")
        return self.cursor.fetchall()

    def update_password(self, id, site, login, password):
        """Обновляет запись в базе данных без хэширования пароля."""
        self.cursor.execute("UPDATE passwords SET site=?, login=?, password=? WHERE id=?", 
                        (site, login, password, id))
        self.conn.commit()

    def delete_password(self, id):
        """Удаляет запись из базы данных."""
        self.cursor.execute("DELETE FROM passwords WHERE id = ?", (id,))
        self.conn.commit()

    def password_exists(self, site):
        """Проверяет, существует ли пароль для данного сайта."""
        self.cursor.execute("SELECT COUNT(*) FROM passwords WHERE site = ?", (site,))
        return self.cursor.fetchone()[0] > 0

    def create_backup(self):
        """Создает резервную копию данных в JSON-файл."""
        data = self.get_all_passwords()
        with self.backup_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def restore_backup(self):
        """Восстанавливает данные из JSON-файла."""
        if self.backup_path.exists():
            with self.backup_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.cursor.execute("DELETE FROM passwords")  # Очищаем таблицу
                for item in data:
                    self.cursor.execute(
                        "INSERT INTO passwords (site, login, password, created_at) VALUES (?, ?, ?, ?)",
                        (item[1], item[2], item[3], item[4])
                    )
                self.conn.commit()

    def delete_backup(self):
        """Удаляет резервный JSON-файл."""
        if self.backup_path.exists():
            self.backup_path.unlink()

    def close(self):
        self.conn.close()