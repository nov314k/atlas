"""Experimental. Do not use."""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout


class LogProgressDialog(QDialog):

    def __init__(self):

        self.log_entry_term = QLineEdit()

    def setup(self):

        self.setMinimumSize(600, 100)
        self.setWindowTitle("Log Progress")
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)
        log_entry_label = QLabel("Log entry:")
        widget_layout.addWidget(log_entry_label)
        widget_layout.addWidget(self.log_entry_term)
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        widget_layout.addWidget(button_box)

    def log_entry(self):

        return self.log_entry_term.text()
