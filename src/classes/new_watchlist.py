from PyQt5.QtWidgets import QDialog, QGroupBox, QSpinBox, QTextEdit, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel
import sys
 
# creating a class
# that inherits the QDialog class
class NewWatchlistEntry(QDialog):
 
    # constructor
    def __init__(self, watchlist_id, movie_id, watchlist_name, movie_name):
        super(NewWatchlistEntry, self).__init__()
        self.watchlist_id = watchlist_id
        self.movie_id = movie_id
 
        # setting window title
        self.setWindowTitle(f"Add {movie_name} to {watchlist_name}")
 
        # setting geometry to the window
        self.setGeometry(100, 100, 400, 300)
 
        # creating a group box
        self.formGroupBox = QGroupBox("Rating and Comment")

        layout = QFormLayout()
        self.inputs = {}

        self.rating = QSpinBox()
        self.rating.setMinimum(0)
        self.rating.setMaximum(5)
        layout.addRow(QLabel("Rating:"), self.rating)

        self.comment = QTextEdit()
        layout.addRow(QLabel("Comment:"), self.comment)
        
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