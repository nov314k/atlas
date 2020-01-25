"""Contains all dialogs used in the application.

Contains classes: PrepareDayDialog, LogProgressDialog, LogExpenseDialog,
AddAdhocTaskDialog.

"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout


class PrepareDayDialog(QDialog):
    """Docstring."""

    def __init__(self, parent=None):
        """Initialize PrepareDayDialog."""

        super().__init__(parent)

    def setup(self, target_day=None, target_month=None, target_year=None):
        """Set up the dialog for preparing a day plan.

        The dialog gets from the user the date (separately day, month, and
        year) for which to prepare a day plan.

        """

        self.setMinimumSize(200, 200)
        self.setWindowTitle("Enter target")
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)

        self.target_day_term = QLineEdit()
        target_day_label = QLabel("Target day:")
        self.target_day_term.setText(target_day)
        widget_layout.addWidget(target_day_label)
        widget_layout.addWidget(self.target_day_term)

        self.target_month_term = QLineEdit()
        target_month_label = QLabel("Target month:")
        self.target_month_term.setText(target_month)
        widget_layout.addWidget(target_month_label)
        widget_layout.addWidget(self.target_month_term)

        self.target_year_term = QLineEdit()
        target_year_label = QLabel("Target year:")
        self.target_year_term.setText(target_year)
        widget_layout.addWidget(target_year_label)
        widget_layout.addWidget(self.target_year_term)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        widget_layout.addWidget(button_box)

    def target_day(self):
        """Return month-day of the date for which to prepare a day plan."""

        return int(self.target_day_term.text())

    def target_month(self):
        """Return month of the date for which to prepare a day plan."""

        return int(self.target_month_term.text())

    def target_year(self):
        """Return year of the date for which to prepare a day plan."""

        return int(self.target_year_term.text())
