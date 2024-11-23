# imports
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from pathlib import Path
import socket
from random import randrange

# create a unique app id for exec file
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'ise.it_database.pc_and_laptops'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def runApp():
        from src.classes.main_window import MainWindow
        window = MainWindow()
        app.exec_()


if __name__ == '__main__':
    # run the app
    try:
        app = QApplication(sys.argv)
    except Exception as e:
        print(e)
    finally:
        sys.exit(runApp())