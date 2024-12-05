
# imports
import os, sys, traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QTabWidget, QToolButton, QWidget, QInputDialog, QHBoxLayout, QVBoxLayout, QLabel, QToolBar, QMessageBox, QAction, QMenu, QLineEdit
from PyQt5.QtGui import QIcon
from pathlib import Path
import json

from src.classes.tab import TabWidget
from src.classes.sql_controller import query_data

class MainWindow(QMainWindow):
    def __init__(self):
        """Build window with task table"""
        super().__init__()
        # set up window
        self.setWindowTitle("Movie Database")
        from src.run import resource_path
        self.setWindowIcon(QIcon(resource_path(Path('data/computer.ico'))))

        # create menu bar widgets
        new_action = QAction("New Watchlist", self)
        self.hide_columns_button = QToolButton()
        self.hide_columns_button.setText("Hide Columns")
        filter_button = QToolButton()
        filter_button.setText("Set Filter")

        # create search bar
        search_label = QLabel("Search: ")
        self.search_bar = QLineEdit()

        # create tabs
        self.tabs = QTabWidget()
        with open("data/main_tables.txt") as file:
            for s in file.readlines():
                (query, name) = s.strip().split(",,,")
                info = query_data(query)
                self.tabs.addTab(TabWidget(self, info, name), name)
        self.tabs.widget(0).actor_menu.triggered.connect(self.goToActor)

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
        watchlists, headers = query_data("SELECT watchlist_id, name FROM watchlists")
        for i, info in enumerate(watchlists):
            temp = QAction(info['name'], self)
            temp.setWhatsThis(str(i+1))
            self.side_bar.addAction(temp)
            entries_info = query_data("SELECT * FROM watchlist_entries WHERE watchlist_id = "+str(info["watchlist_id"]))
            self.stacked_widget.addWidget(TabWidget(self, entries_info, name))

        self.setColumnsMenu()
        self.hide_columns_button.setPopupMode(QToolButton.InstantPopup)

        # connect actions
        new_action.triggered.connect(self.newWatchlist)
        self.search_bar.textChanged.connect(self.tabs.currentWidget().proxy.setFilterFixedString)
        self.tabs.currentChanged.connect(self.changeCurrentTab)
        self.side_bar.actionTriggered.connect(self.sideBarClicked)

        # add actions and widgets to a menu bar
        menubar = QToolBar()
        menu_actions = [new_action]
        menu_widgets = [self.hide_columns_button, filter_button]
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
        index = self.tabs.currentWidget().columns.index(checkbox.text()) ############### needs fixing
        self.tabs.currentWidget().view.setColumnHidden(index, checkbox.isChecked()==False)

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
            else:
                self.search_bar.textChanged.connect(self.stacked_widget.currentWidget().proxy.setFilterFixedString)
        except Exception as e:
            self.showError(action, e)

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
        new_name, success = QInputDialog.getText(self, "New Watchlist", "Enter watchlist name:")
        if success and new_name in self.watchlists:
            QMessageBox.critical(None, 'Name Taken', "There is already a watchlist with the name " + new_name + ".")
        elif success:
            self.watchlists.append(new_name)
            temp = QAction(new_name, self)
            temp.setWhatsThis(str(len(self.watchlists)))
            self.side_bar.addAction(temp)
            # add watchlist table to the database

            # Data to be written
            dictionary = {
                "Movie": [],
                "Comment": [],
                "Rating": []
            }
            
            # Serializing json
            json_object = json.dumps(dictionary, indent=4)
            
            # Writing to sample.json
            new_file_path = "data/watchlists/"+new_name.replace(' ', '_')+".json"
            with open(new_file_path, "w") as outfile:
                outfile.write(json_object)

            self.stacked_widget.addWidget(TabWidget(self, new_file_path)) # dummy value
    
    def setColumnsMenu(self):
    # dynamically add actions to visible_columns_menu
        visible_columns_menu = QMenu()
        for i, column in enumerate(self.tabs.currentWidget().columns): # add a qaction to menu per column
            temp = QAction(column, self)
            temp.setCheckable(True)
            if self.tabs.currentWidget().view.isColumnHidden(i) == True:
                temp.setChecked(False)
            else:
                temp.setChecked(True)
            visible_columns_menu.addAction(temp)

        visible_columns_menu.triggered.connect(self.columnsChange)

        # attach menus to qtoolbuttons
        self.hide_columns_button.setMenu(visible_columns_menu)

    def goToActor(self, action):
        print(action.whatsThis())
        return

