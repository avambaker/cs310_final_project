from PyQt5.QtWidgets import QDialog, QGroupBox, QSpinBox, QComboBox, QLineEdit, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel
import sys
 
# creating a class
# that inherits the QDialog class
class FilterDialog(QDialog):
 
    # constructor
    def __init__(self, data):
        super(FilterDialog, self).__init__()

 
        # setting window title
        self.setWindowTitle("Filter")
 
        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)
 
        # creating a group box
        self.formGroupBox = QGroupBox("Filter Values")

        layout = QFormLayout()
        self.inputs = {}

        for (title, datatype) in data:
            line_edit = QLineEdit()
            layout.addRow(QLabel(title), line_edit)
            self.inputs[title] = line_edit
        
        self.formGroupBox.setLayout(layout)
 
        # creating a dialog button for ok and cancel
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
 
        # adding action when form is rejected
        self.buttonBox.rejected.connect(self.reject)
 
        # creating a vertical layout
        mainLayout = QVBoxLayout()
 
        # adding form group box to the layout
        mainLayout.addWidget(self.formGroupBox)
 
        # adding button box to the layout
        mainLayout.addWidget(self.buttonBox)
 
        # setting lay out
        self.setLayout(mainLayout)