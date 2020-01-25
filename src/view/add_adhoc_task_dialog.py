"""Contains all dialogs used in the application.

Contains classes: PrepareDayDialog, LogProgressDialog, LogExpenseDialog,
AddAdhocTaskDialog.

"""

from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout


class AddAdhocTaskDialog(QDialog):
    """Docstring."""

    def __init__(self, parent=None):
        """Initialize AddAdhocTask Dialog."""

        super().__init__(parent)

    def setup(self):
        """Set up the dialog to add an ad hoc task."""

        self.setMinimumSize(600, 100)
        self.setWindowTitle("Add an ad hoc task")
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)

        adhoc_task_label = QLabel("Ad hoc task:")
        widget_layout.addWidget(adhoc_task_label)

        self.adhoc_task_term = QLineEdit()
        widget_layout.addWidget(self.adhoc_task_term)
        self.adhoc_task_term.setFocus()

        duration_label = QLabel("dur:")
        widget_layout.addWidget(duration_label)

        self.duration_term = QLineEdit()
        widget_layout.addWidget(self.duration_term)
        self.duration_term.setText("0")

        self.finished_term = QCheckBox("Task aready finished", self)
        widget_layout.addWidget(self.finished_term)

        self.plus_work_term = QCheckBox("This is a +work task", self)
        widget_layout.addWidget(self.plus_work_term)

        tags_label = QLabel("Tags (please include '+'):")
        widget_layout.addWidget(tags_label)

        self.tags_term = QLineEdit()
        self.tags_term.setText("+adhoc")
        widget_layout.addWidget(self.tags_term)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        widget_layout.addWidget(button_box)

    def adhoc_task(self):
        """Get entered values from the add an ad hoc task dialog."""

        return [self.adhoc_task_term.text(), self.duration_term.text(),
                self.tags_term.text(), self.finished_term.isChecked(),
                self.plus_work_term.isChecked()]
