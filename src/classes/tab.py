from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QDialog, QMessageBox, QLineEdit, QLabel, QTextEdit, QSpinBox, QInputDialog, QAction, QMenu, QTableView
from PyQt5.QtGui import QCursor
from src.classes.mysql_model import MySQLModel

import pandas as pd
from src.classes.mysql_model import MySQLModel
from src.run import resource_path
from pathlib import Path

class TabWidget(QWidget): 
    def __init__(self, parent, data, name): 
        super(QWidget, self).__init__(parent)
        self.default_data = data
        self.name = name
        self.watchlist_menu = QMenu()
        self.person_menu = QMenu()

        if type(data) == str:
            data = pd.read_json(resource_path(Path(data)))
            #self.model = PandasModel(data)
        else:
            if data:
                self.model = MySQLModel(data)
            else:
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
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # resize columns and hide certain columns
        for i in range(self.view.horizontalHeader().count()):
            self.view.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        # hide columns
        self.formatColumns()

    
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
            self.watchlistMenu(row, model_qindex.column(), data)
        
        if self.name == 'movie_view' and 'name' in col_name and data is not None:
            self.personMenu(row, model_qindex.column(), col_name, data)
        
        if '_view' not in self.name and col_name == 'movie_name':
            self.editMenu(row, model_qindex.column())
    
    def watchlistMenu(self, row, col, data):
        self.watchlist_menu.clear()
        # add actions
        from src.classes.sql_controller import query_data
        watchlists = query_data("Select watchlist_id, name from watchlists;", get_tuples=True)
        movie_id = str(self.model.index(row, col-1).data())
        for (id, name) in watchlists:
            watchlist_option = QAction(f"Add to {name}", self.watchlist_menu)
            watchlist_option.setData((id, movie_id, name, data))
            self.watchlist_menu.addAction(watchlist_option)
        # show menu
        action = self.watchlist_menu.exec_(QCursor.pos())
    
    def editMenu(self, row, col):
        temp = self.model.index(row, col-1)
        movie_id = str(temp.data())
        watchlist_id = str(self.model.index(row, col-2).data())
        edit_menu = QMenu()
        edit = QAction("Edit")
        edit.setData((watchlist_id, movie_id, row))
        delete = QAction("Delete")
        delete.setData((watchlist_id, movie_id, row))
        edit_menu.addAction(edit)
        edit_menu.addAction(delete)
        edit_menu.triggered.connect(self.deleteOrEditEntry)
        edit_menu.exec_(QCursor.pos())
    
    def deleteOrEditEntry(self, action):
        (watchlist_id, movie_id, row) = action.data()
        if action.text() == "Delete":
            self.deleteEntry(watchlist_id, movie_id, row)
        else:
            self.editEntry(watchlist_id, movie_id, row)

    def deleteEntry(self, watchlist_id, movie_id, row):
        from src.classes.sql_controller import query_data
        query = "DELETE FROM watchlist_entries WHERE watchlist_id = %s AND movie_id = %s"
        query_data(query, params=(watchlist_id, movie_id))
        self.model.removeRow(row)
        row_count = self.model.rowCount()
        self.view.rowCountChanged(row_count - 1, row_count)
    
    def editEntry(self, watchlist_id, movie_id, row_index):
        row = self.model.getRow(row_index)
        dialog = QInputDialog()
        dialog.setWindowTitle(f"Edit {row['movie_name']} Entry")
        dialog.show()
        # hide default QLineEdit
        dialog.findChild(QLineEdit).hide()
        dialog.findChild(QLabel).hide()
        # adjust layout
        dialog.layout().insertWidget(1, QLabel("Rating:"))
        rating_box = QSpinBox()
        rating_box.setMinimum(0)
        rating_box.setMaximum(5)
        rating_box.setValue(row['rating'])
        dialog.layout().insertWidget(2, rating_box)
        dialog.layout().insertWidget(3, QLabel("Comment:"))
        comment_text = QTextEdit()
        comment_text.insertPlainText(row["comment"])
        dialog.layout().insertWidget(4, comment_text)
        ret = dialog.exec_() == QDialog.Accepted
        if ret:
            from src.classes.sql_controller import query_data
            query = "UPDATE watchlist_entries SET rating = %s, comment = %s WHERE watchlist_id = %s AND movie_id = %s"
            new_rating = rating_box.value()
            new_comment = comment_text.toPlainText()
            try:
                query_data(query, params=(new_rating, new_comment, watchlist_id, movie_id))
                self.model.setData(self.model.index(row_index, self.model.getColIndex("rating")), new_rating)
                self.model.setData(self.model.index(row_index, self.model.getColIndex("comment")), new_comment)
            except Exception as e:
                QMessageBox.critical(self, "Error", "Uh oh! Looks like your formatting was off. Try again.")
                print(e)
    
    def personMenu(self, row, col, col_name, data):
        tab_names = {'star_name': ('Actors', 1, 'actor_id'), 'director_name': ('Directors', 2, 'director_id'), 'producer_name': ('Production Companies', 3, 'company_id')}
        (tab_name, tab_index, new_col_name) = tab_names[col_name]
        self.person_menu.clear()
        # add actions
        option = QAction("Go To " + data + " in " + tab_name + " Tab")
        option.setWhatsThis(str(self.model.index(row, col-1).data()) + "," + str(tab_index) + "," + new_col_name)
        self.person_menu.addAction(option)
        # show menu
        action = self.person_menu.exec_(QCursor.pos())

    def findPerson(self, person_id, col_name):
        self.setFilter()
        (row_index, col_index) = self.model.getRowIndexFromVal(person_id, col_name)
        qindex = self.getRowFromModel(row_index, col_index)
        self.view.selectRow(qindex.row())
    
    def getRowFromModel(self, row, col):
        qindex = self.model.index(row, col)
        proxy_index = self.proxy.mapFromSource(qindex)
        return proxy_index
    
    def setFilter(self, data=None):
        if data:
            self.model.resetModel(data)
        else:
            self.model.resetModel(self.default_data)
        self.columns = self.model.getColumnNames()
        self.formatColumns()
    
    def formatColumns(self):
        for i, val in enumerate(self.columns):
            if '_id' in val:
                self.view.setColumnHidden(i, True)