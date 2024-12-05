from PyQt5.QtCore import QAbstractTableModel, Qt

class MySQLModel(QAbstractTableModel):
    def __init__(self, data=None, headers=None):
        super(MySQLModel, self).__init__()
        self._data = data if data else []
        self._headers = headers if headers else []

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