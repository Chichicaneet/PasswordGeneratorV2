import sys
# import os
from PySide6.QtWidgets import QApplication
# from PySide6.QtGui import QIcon
from ui import PasswordGeneratorApp

# def get_icon_path():
#     if getattr(sys, 'frozen', False):
#         # Если приложение собрано в exe
#         return os.path.join(sys._MEIPASS, 'app_icon.ico')
#     else:
#         # Если приложение запускается из исходного кода
#         return os.path.join(os.path.dirname(__file__), 'app_icon.ico')

if __name__ == "__main__":
    # Получить абсолютный путь к иконке
    # icon_path = os.path.join(os.path.dirname(__file__), 'app_icon.ico')
    # icon_path = get_icon_path()  
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(icon_path))
    window = PasswordGeneratorApp()
    # window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    sys.exit(app.exec())