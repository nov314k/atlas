from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout


class PrepareDayDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

    def setup(self, target_day=None, target_month=None, target_year=None):

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

        return int(self.target_day_term.text())

    def target_month(self):

        return int(self.target_month_term.text())

    def target_year(self):

        return int(self.target_year_term.text())
