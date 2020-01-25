"""Contains all dialogs used in the application.

Contains classes: PrepareDayDialog, LogProgressDialog, LogExpenseDialog,
AddAdhocTaskDialog.

"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
# from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
#                             QLabel, QLineEdit, QVBoxLayout)


class LogProgressDialog(QDialog):
    """Dialog for logging progress (the main log)."""

    def __init__(self):
        """Docstring."""

        self.log_entry_term = QLineEdit()

    def setup(self):
        """Docstring."""

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
        """Docstring."""

        return self.log_entry_term.text()
