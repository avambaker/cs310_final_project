
# imports
import os, sys, traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QDialog, QSpinBox, QTextEdit, QTabWidget, QToolButton, QWidget, QInputDialog, QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QMessageBox, QAction, QMenu, QLineEdit
from PyQt5.QtGui import QIcon
from pathlib import Path
import json

from src.classes.tab import TabWidget
from src.classes.sql_controller import *

class MainWindow(QMainWindow):
    def __init__(self):
        """Build window with task table"""
        super().__init__()
        attempt = connect_to_database()
        if attempt is None:
            loaded = self.loadSQLData()
            print("Return of method loadSQLData:", loaded)
            if not loaded:
                print("Loading ddl failed...")
                sys.exit(1)
        else:
            attempt.close()
        # set up window
        self.setWindowTitle("Movie Database")
        from src.run import resource_path
        self.setWindowIcon(QIcon(resource_path(Path('data/computer.ico'))))

        # create menu bar widgets
        new_action = QAction("New Watchlist", self)
        self.hide_columns_button = QToolButton()
        self.hide_columns_button.setText("Hide Columns")
        self.filter_button = QToolButton()
        self.filter_button.setText("Set Filter")

        # create search bar
        search_label = QLabel("Search: ")
        self.search_bar = QLineEdit()

        # create tabs
        self.tabs = QTabWidget()
        with open("data/main_tables.txt") as file:
            for s in file.readlines():
                (query, name) = s.strip().split(",,,")
                table_name = query.split(" ")[-1]
                info = query_data(query)
                self.tabs.addTab(TabWidget(self, info, table_name), name)
        self.tabs.widget(0).person_menu.triggered.connect(self.goToID)
        self.tabs.widget(0).watchlist_menu.triggered.connect(self.addToWatchlist)
        self.tabs.setCurrentIndex(0)

        # create stacked widget
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.tabs)
        self.stacked_widget.setCurrentIndex(0)

        # create side bar
        self.side_bar = QToolBar(self)
        self.database_button = QAction("Database")
        self.database_button.setWhatsThis("0")
        self.side_bar.addAction(self.database_button)
        self.side_bar.addSeparator()

        # set up watchlists
        self.watchlists = query_data("SELECT watchlist_id, name, description FROM watchlists")
        if type(self.watchlists) is dict:
            self.watchlists = []
        for i, info in enumerate(self.watchlists, start=1):
            self.createWatchlistWidget(info['watchlist_id'], info['name'], info['description'], i)

        # set up hide columns button
        self.setColumnsMenu()
        self.hide_columns_button.setPopupMode(QToolButton.InstantPopup)

        # connect actions
        new_action.triggered.connect(self.newWatchlist)
        self.search_bar.textChanged.connect(self.tabs.currentWidget().proxy.setFilterFixedString)
        self.tabs.currentChanged.connect(self.changeCurrentTab)
        self.side_bar.actionTriggered.connect(self.sideBarClicked)
        self.filter_button.clicked.connect(self.setFilter)

        # add actions and widgets to a menu bar
        self.menubar = QToolBar()
        menu_actions = [new_action]
        menu_widgets = [self.hide_columns_button, self.filter_button]
        for action in menu_actions:
            self.menubar.addAction(action)
        for widget in menu_widgets:
            self.menubar.addWidget(widget)

        # create horizontal search bar layout
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(10)

        # vertically stack search bar with menubar and view
        vbox = QVBoxLayout()
        vbox.addWidget(self.menubar)
        vbox.addLayout(search_layout)
        vbox.addWidget(self.stacked_widget)
        vbox.setContentsMargins(0,0,0,0)

        # put layout in widget and place widget on window
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)
        self.tabs.currentWidget().model.layoutChanged.emit()
        self.addToolBar(Qt.LeftToolBarArea, self.side_bar)

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
    
    def columnsChange(self, checkbox):
        """Toggle if a column is hidden or shown"""
        if self.stacked_widget.currentIndex() == 0:
            index = self.tabs.currentWidget().columns.index(checkbox.text())
            self.tabs.currentWidget().view.setColumnHidden(index, checkbox.isChecked()==False)
        else:
            index = self.stacked_widget.currentWidget().tab.columns.index(checkbox.text())
            self.stacked_widget.currentWidget().tab.view.setColumnHidden(index, checkbox.isChecked()==False)

    def changeCurrentTab(self):
        self.search_bar.clear()
        self.search_bar.textChanged.connect(self.tabs.currentWidget().proxy.setFilterFixedString)
        self.setColumnsMenu()
    
    def sideBarClicked(self, action):
        try:
            index = int(action.whatsThis())
            self.stacked_widget.setCurrentIndex(index)
            self.search_bar.clear()
            if index == 0:
                self.search_bar.textChanged.connect(self.tabs.currentWidget().proxy.setFilterFixedString)
                self.menubar.actions()[2].setVisible(True)
            else:
                self.search_bar.textChanged.connect(self.stacked_widget.currentWidget().tab.proxy.setFilterFixedString)
                self.menubar.actions()[2].setVisible(False)
            self.setColumnsMenu()
        except Exception as e:
            self.showError("side bar clicked", e)

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
    
    def newWatchlist(self):
        success, (name, description) = self.get_text_values("Create a new watchlist.", ["Name", "Description"], [QLineEdit(), QTextEdit()], self, "New Watchlist")
        if success and name in self.watchlists:
            QMessageBox.critical(None, 'Name Taken', "There is already a watchlist with the name " + name + ".")
        elif success:
            # add to watchlists info list
            new_dict = {"watchlist_id": len(self.watchlists)+1, "name": name, "description": description}
            self.watchlists.append(new_dict)
            # create id
            # add watchlist to watchlist table in database
            query = "INSERT INTO watchlists (name, description) VALUES (%s, %s);"
            query_data(query, params=(name, description))
            # add watchlist to sidebar
            self.createWatchlistWidget(len(self.watchlists), name, description, len(self.watchlists))
    
    def setColumnsMenu(self):
    # dynamically add actions to visible_columns_menu
        visible_columns_menu = QMenu()
        if self.stacked_widget.currentIndex() == 0:
            columns = self.tabs.currentWidget().columns
        else:
            columns = self.stacked_widget.currentWidget().tab.columns
        for i, column in enumerate(columns): # add a qaction to menu per column
            if "_id" not in column:
                temp = QAction(column, self)
                temp.setCheckable(True)
                if self.tabs.currentWidget().view.isColumnHidden(i) == True:
                    temp.setChecked(False)
                else:
                    temp.setChecked(True)
                visible_columns_menu.addAction(temp)

        visible_columns_menu.triggered.connect(self.columnsChange)

        filter_menu = QMenu()
        filter_menu.addAction(QAction("test"))

        # attach menus to qtoolbuttons
        self.hide_columns_button.setMenu(visible_columns_menu)

    def goToID(self, action):
        (person_id, tab_index, col_name) = action.whatsThis().split(",")
        self.tabs.setCurrentIndex(int(tab_index))
        self.tabs.currentWidget().findPerson(int(person_id), col_name)

    def setFilter(self):
        columns = query_data("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'testmoviedb' AND TABLE_NAME = '%s';" % self.tabs.currentWidget().name, get_tuples = True)
        columns = [column for column in columns if '_id' not in column]
        success, values = self.get_text_values("Set Filter", columns, [QLineEdit() for _ in range(len(columns))], self, title = "Set Filter")
        if success:
            values = [None if v == "" else v for v in values]
            print(columns)
            procedure_name = "filter_" + self.tabs.currentWidget().name
            from src.classes.sql_controller import callProcedure
            try:
                new_data = callProcedure(procedure_name, values)
                self.tabs.currentWidget().setFilter(new_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", "Uh oh! Looks like your formatting was off. Try again.")
                print(e)
        
    
    def addToWatchlist(self, action):
        (watchlist_id, movie_id, watchlist_name, movie_name) = action.data()
        row_index = -1
        widget_index = -1
        col_index = -1
        for i in range(1, self.stacked_widget.count()):
            if self.stacked_widget.widget(i).id == watchlist_id:
                row_index, col_index = self.stacked_widget.widget(i).tab.model.getRowIndexFromVal(int(movie_id), "movie_id")
                widget_index = i
        if row_index == -1:
            rating_box = QSpinBox()
            rating_box.setMinimum(0)
            rating_box.setMaximum(5)
            success, (rating, comment) = self.get_text_values("Write a comment and rating!", ["Rating", "Comment"], [rating_box, QTextEdit()], self, f"Add {movie_name} to {watchlist_name}")
            if success:
                # check if they added a comment
                if comment == "": comment = "NA"
                # add entry to sql table
                query = "INSERT INTO watchlist_entries (movie_id, watchlist_id, rating, comment) VALUES (%s, %s, %s, %s);"
                query_data(query, params=(movie_id, watchlist_id, rating, comment))
                # locate watchlist in stacked_widget and update
                for i in range(1, self.stacked_widget.count()):
                    if self.stacked_widget.widget(i).tab.name == watchlist_name:
                        entries_info = query_data("CALL get_watchlist_entries(%s);", params=watchlist_id)
                        self.stacked_widget.widget(i).tab.setFilter(entries_info)
        else:
            find_entry = QMessageBox()
            find_entry.setIcon(QMessageBox.Information)
            find_entry.setText(f"{movie_name} is already in {watchlist_name}. Would you like to go to it?")
            find_entry.setWindowTitle("Already exists")
            find_entry.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            #find_entry.buttonClicked.connect(self.openEntry)
            ret_val = find_entry.exec()
            if ret_val == QMessageBox.Ok:
                self.stacked_widget.setCurrentIndex(widget_index)
                self.search_bar.clear()
                self.search_bar.textChanged.connect(self.stacked_widget.currentWidget().tab.proxy.setFilterFixedString)
                self.menubar.actions()[2].setVisible(False)
                self.setColumnsMenu()
                view_index = self.stacked_widget.currentWidget().tab.getRowFromModel(row_index, col_index)
                self.stacked_widget.currentWidget().tab.view.selectRow(view_index.row())
    
    def get_text_values(self, label, arg_names, editors, parent=None, title=""):
        dialog = QInputDialog()
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.show()
        # hide default QLineEdit
        dialog.findChild(QLineEdit).hide()

        count = 1
        for i, text in enumerate(arg_names):
            label = QLabel(text+":")
            dialog.layout().insertWidget(count, label)
            dialog.layout().insertWidget(count + 1, editors[i])
            count += 2

        ret = dialog.exec_() == QDialog.Accepted
        vals = []
        for editor in editors:
            if type(editor) is QSpinBox:
                vals.append(editor.value())
            elif type(editor) is QTextEdit:
                vals.append(editor.toPlainText())
            elif type(editor) is QLineEdit:
                vals.append(editor.text())
        return ret, vals
    
    def createWatchlistWidget(self, watchlist_id, name, description, index):
        temp = QAction(name, self)
        temp.setWhatsThis(str(index))
        self.side_bar.addAction(temp)
        entries_info = query_data("CALL get_watchlist_entries(%s);", params=watchlist_id)
        watchlist_widget = QWidget()
        watchlist_widget.id = watchlist_id
        layout = QVBoxLayout()
        layout.addWidget(QLabel(name + ": " + description))
        watchlist_widget.tab = TabWidget(watchlist_widget, entries_info, name)
        layout.addWidget(watchlist_widget.tab)
        watchlist_widget.setLayout(layout)
        self.stacked_widget.addWidget(watchlist_widget)
    
    def getPassword(self):
        text, ret = QInputDialog.getText(None, "SQL Password","Please enter your SQL password below. Double check it, as you cannot change it later.", QLineEdit.Normal, "")
        if text and ret:
            return text
        elif ret:
            return ""
        else:
            self.getPassword()
    
    def loadSQLData(self):
        with open('data/sql_password.txt') as f:
            n = len(f.readlines())
        if n <= 1:
            new_password = self.getPassword()
            setPassword(new_password)
        success = create_database('database_files/movie_ddl.sql')
        print("create database:", success)
        try:
            loop_csv("database_files/parent_tables")
            loop_csv("database_files/dependent_tables")
            with open('data/sql_password.txt', 'a') as f:
                f.write("\nReady")
            return True
        except Exception as e:
            print(e)
            return False
    

