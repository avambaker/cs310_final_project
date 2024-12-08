from PyQt5.QtCore import QAbstractTableModel, Qt

class MySQLModel(QAbstractTableModel):
    def __init__(self, data=None):
        super(MySQLModel, self).__init__()
        self._data = data if data else []
        self._headers = list(data[0].keys()) if data else []

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self._data[row][self._headers[col]]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            if orientation == Qt.Vertical:
                return section + 1
        return None
    
    def getColumnNames(self):
        return self._headers
    
    def getRowIndexFromVal(self, val, col_name):
        for i, row in enumerate(self._data):
            if row[col_name] == val:
                return (i, list(row.keys()).index(col_name))
        return (-1, -1)
    
    def removeRow(self, index):
        del self._data[index]
    
    def resetModel(self, data):
        self.beginResetModel()
        self._data = data
        self._headers = list(data[0].keys()) if data else []
        self.endResetModel()
    
    def getColIndex(self, col_name):
        return self._headers.index(col_name)
    
    def getRow(self, index):
        return self._data[index]
    
    def updateCell(self, row_index, col_name, new_value):
        self._data[row_index][col_name] = new_value
    
    def setData(self, index, value, role = Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._data[index.row()][self._headers[index.column()]] = value
            # Emit dataChanged signal
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        return False