from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QMainWindow, QToolButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QMessageBox, QHeaderView, QAction, QMenu, QTableView, QLineEdit
from PyQt5.QtGui import QCursor, QIcon

class MyTabWidget(QWidget): 
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 