
# imports
import os, sys, traceback

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QMainWindow, QToolButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QMessageBox, QHeaderView, QAction, QMenu, QTableView, QLineEdit
from PyQt5.QtGui import QCursor, QIcon
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import json

from src.classes.pandas_model import PandasModel

class MainWindow(QMainWindow):
    def __init__(self):
        """Build window with task table"""
        super().__init__()
        # set up window
        self.setWindowTitle("Task Tracker")
        from src.run import resource_path
        self.setWindowIcon(QIcon(resource_path(Path('data/computer.ico'))))

        # create data model and save column names
        task_data = pd.read_json(resource_path(Path('data/task_data.json')))
        self.model = PandasModel(task_data)
        self.columns = self.model.getColumnNames()

        # create proxy models (used for filtering)
        self.status_proxy = QSortFilterProxyModel()
        self.status_proxy.setSourceModel(self.model)
        self.status_proxy.setFilterKeyColumn(self.columns.index('Status'))
        self.status_proxy.setFilterFixedString('Active')
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.status_proxy)
        self.proxy.setFilterKeyColumn(-1) # set the column to filter by as all
        self.proxy.setFilterCaseSensitivity(False)

        # create view model
        self.view = QTableView()
        self.view.setModel(self.proxy)
        self.view.installEventFilter(self)
        self.view.verticalHeader().hide() # don't show indexes
        self.view.setSortingEnabled(True)
        self.view.setTextElideMode(Qt.ElideRight)
        self.view.setWordWrap(True)

        # resize columns and hide certain columns
        for i in range(self.view.horizontalHeader().count()):
            self.view.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            if self.columns[i] in ['Details']:
                self.view.setColumnHidden(i, True)

        # create menu bar widgets
        new_action = QAction("New Watchlist", self)
        hide_columns_button = QToolButton()
        hide_columns_button.setText("Hide Columns")
        visible_columns_menu = QMenu()

        # create search bar
        search_label = QLabel("Search: ")
        self.search_bar = QLineEdit()

        # get data validation columns
        with open(resource_path(Path('data/type_data.json')), 'r') as f:
            options = json.load(f)

        # dynamically add actions to visible_columns_menu
        for i, column in enumerate(self.columns): # add a qaction to menu per column
            temp = QAction(column, self)
            temp.setCheckable(True)
            if self.view.isColumnHidden(i) == True:
                temp.setChecked(False)
            else:
                temp.setChecked(True)
            visible_columns_menu.addAction(temp)

        # attach menus to qtoolbuttons
        hide_columns_button.setMenu(visible_columns_menu)
        hide_columns_button.setPopupMode(QToolButton.InstantPopup)

        # connect actions
        #new_action.triggered.connect()
        self.search_bar.textChanged.connect(self.proxy.setFilterFixedString)
        visible_columns_menu.triggered.connect(self.columnsChange)

        # add actions and widgets to a menu bar
        menubar = QToolBar()
        menu_actions = [new_action]
        menu_widgets = [hide_columns_button]
        for action in menu_actions:
            menubar.addAction(action)
        for widget in menu_widgets:
            menubar.addWidget(widget)

        # create horizontal search bar layout
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(10)

        # vertically stack search bar with menubar and view
        vbox = QVBoxLayout()
        vbox.addWidget(menubar)
        vbox.addLayout(search_layout)
        vbox.addWidget(self.view)
        vbox.setContentsMargins(0,0,0,0)

        # put layout in widget and place widget on window
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)
        self.model.layoutChanged.emit()
        self.showMaximized()

        # locate user's download folder
        if os.name == "nt":
            self.DOWNLOAD_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads"
        else:  # PORT: For *Nix systems
            self.DOWNLOAD_FOLDER = f"{os.getenv('HOME')}/Downloads"

    def getConfirmation(self, action, task_name, message):
        """Ask user if they would like to complete the action"""
        # create message box
        reply = QMessageBox.critical(self, 'Confirm '+action.title(), 
                        "Are you sure you want to " + action  +" " + task_name + "?"+message, QMessageBox.Yes, QMessageBox.Cancel)

        # return reply
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def closeEvent(self, event):
        """Ask user if they would like to save unsaved changes"""
        # check if model is dirty or not
        if self.model.isDirty() == False:
            # close
            event.accept()
        else:
            # ask user if they want to save changes
            reply = QMessageBox.question(self, 'Unsaved Changes', 
                            "Would you like to save your changes before exiting?", QMessageBox.Yes, QMessageBox.No)
            # save if yes accepted
            if reply == QMessageBox.Yes:
                self.save()
            else:
                second_confirmation = QMessageBox.question(self, 'Discard Changes', 
                            "Are you sure you want to delete all changes and exit?", QMessageBox.Yes, QMessageBox.Cancel)
                if second_confirmation == QMessageBox.Cancel:
                    event.ignore()
                else: event.accept()
    
    def regMenu(self, row):
        """Context menu allows you to clone a task or mark it as completed"""
        # create menu
        menu = QMenu()
        # add actions
        example_action = menu.addAction("Example Option")
        # show menu
        action = menu.exec_(QCursor.pos())
            
        # if user selects mark completed
        if action == example_action:
            print("example")
    
    def contextMenuEvent(self, event):
        """Handles right click events"""
        # get row clicked on
        view_index = self.view.selectionModel().currentIndex()
        # map row to proxy
        proxy_index = self.proxy.index(view_index.row(), view_index.column())
        # check validity of proxy index
        if not proxy_index.isValid():
            QMessageBox.critical(None, 'Error', 'The index clicked was invalid.')
            return
        # map row to status_proxy
        status_qindex = self.proxy.mapToSource(proxy_index)
        # check validity of status_qindex
        if not status_qindex.isValid():
            QMessageBox.critical(None, 'Error', 'The index clicked was invalid.')
            return
        # map row to model
        model_qindex = self.status_proxy.mapToSource(status_qindex)
        # check validity of model index
        if not model_qindex.isValid():
            QMessageBox.critical(None, 'Error', 'The index clicked was invalid.')
            return

        # get row index and column name
        row = model_qindex.row()
        col_name = self.columns[model_qindex.column()]

        self.regMenu(row)
    
    def columnsChange(self, checkbox):
        """Toggle if a column is hidden or shown"""
        index = self.columns.index(checkbox.text())
        self.view.setColumnHidden(index, checkbox.isChecked()==False)

    def showError(self, action, e):
        """Print an error message"""
        # get name of function which caused the error
        try: 
            tb = sys.exc_info()[-1]
            stk = traceback.extract_tb(tb, 1)
            fname = stk[0][2]
        except: fname = 'Could not locate function'

        # format message with traceback and function name
        template = "Function Called: {0} \n \n {1}"
        try:
            message = template.format(fname, traceback.format_exc())
        except: 
            message = template.format(fname, 'Error: \n' + str(e))

        QMessageBox.critical(None, 'Error ' + action, message)
