# imports
import sys
import os
from PyQt5.QtWidgets import QApplication, QInputDialog, QDialog, QLineEdit
from pathlib import Path
import socket
from random import randrange
from src.classes.sql_controller import *

# create a unique app id for exec file
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'moviedatabase'
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

def getPassword():
    text, ret = QInputDialog.getText(None, "SQL Password","Please enter your SQL password below. Double check it, as you cannot change it later.", QLineEdit.Normal, "")
    if text and ret:
        return text
    else:
        getPassword()

def loadSQLData():
    if fetchPassword() == "":
        new_password = getPassword()
        setPassword(new_password)
    success = create_database('database_files/movie_ddl.sql')
    print("create database:", success)
    try:
        loop_csv("database_files/parent_tables")
        loop_csv("database_files/dependent_tables")
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    # run the app
    try:
        app = QApplication(sys.argv)
        """attempt = connect_to_database()
        if attempt is None:
            loaded = loadSQLData()
        else:
            attempt.close()"""
    except Exception as e:
        print(e)
    finally:
        sys.exit(runApp())