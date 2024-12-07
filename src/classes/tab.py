from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QAction, QMenu, QTableView
from PyQt5.QtGui import QCursor
from src.classes.mysql_model import MySQLModel

import pandas as pd
from src.classes.mysql_model import MySQLModel
from src.run import resource_path
from pathlib import Path

class TabWidget(QWidget): 
    def __init__(self, parent, file_path, name): 
        super(QWidget, self).__init__(parent)
        self.name = name

        if type(file_path) == str:
            data = pd.read_json(resource_path(Path(file_path)))
            #self.model = PandasModel(data)
        else:
            if file_path:
                self.model = MySQLModel(file_path[0], file_path[1])
            else:
                print("else else")
                # self.model = PandasModel(pd.DataFrame(data={}))
                self.model = MySQLModel(data = {})
        self.columns = self.model.getColumnNames()

        # create proxy models (used for filtering)
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
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
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.actor_menu = QMenu()

    
    def contextMenuEvent(self, event):
        """Handles right click events"""
        # get row clicked on
        view_index = self.view.selectionModel().currentIndex()
        # map row to proxy
        proxy_index = self.proxy.index(view_index.row(), view_index.column())
        # check validity of proxy index
        if not proxy_index.isValid():
            #QMessageBox.critical(None, 'Error', 'The index clicked was invalid.')
            return
        # map row to model
        model_qindex = self.proxy.mapToSource(proxy_index)
        # check validity of model index
        if not model_qindex.isValid():
            #QMessageBox.critical(None, 'Error', 'The index clicked was invalid.')
            return

        # get row index and column name
        row = model_qindex.row()
        col_name = self.columns[model_qindex.column()]
        data = model_qindex.data()

        if col_name == 'title' and data is not None:
            self.watchlistMenu(row, col_name, data)
        
        if col_name == 'star' and data is not None:
            self.actorMenu(row, model_qindex.column(), data)
    
    def watchlistMenu(self, row, col_name, data):
        menu = QMenu()
        # add actions
        example_action = menu.addAction("Add to... [insert watchlist names]")
        # show menu
        action = menu.exec_(QCursor.pos())
    
    def actorMenu(self, row, col, data):
        self.actor_menu.clear()
        # add actions
        option = QAction("Go To " + data + " in Actor Tab")
        option.setWhatsThis(str(self.model.index(row, col-1).data()))
        self.actor_menu.addAction(option)
        # show menu
        action = self.actor_menu.exec_(QCursor.pos())
